using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using FlowPdf.Models;
using FlowPdf.Fluent;

namespace FlowPdf.Client
{
    public class FlowPdfClient : IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly bool _ownsHttpClient;
        private readonly string _baseUrl;
        private readonly string _apiKey;

        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            PropertyNamingPolicy = null,
            DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
        };

        public FlowPdfClient(string baseUrl, string apiKey, HttpClient? httpClient = null)
        {
            _baseUrl = baseUrl.TrimEnd('/');
            _apiKey = apiKey ?? throw new ArgumentNullException(nameof(apiKey));

            if (httpClient == null)
            {
                _httpClient = new HttpClient();
                _ownsHttpClient = true;
            }
            else
            {
                _httpClient = httpClient;
                _ownsHttpClient = false;
            }
        }

        private HttpRequestMessage CreateRequest(HttpMethod method, string path, HttpContent? content = null)
        {
            var url = $"{_baseUrl}{path}";
            var request = new HttpRequestMessage(method, url);
            request.Headers.Add("X-API-Key", _apiKey);
            if (content != null)
            {
                request.Content = content;
            }
            return request;
        }

        public async Task<byte[]> GeneratePdfAsync(DocumentDefinition document, object? data = null, CancellationToken cancellationToken = default)
        {
            var payload = new ReportPayload
            {
                Document = document,
                Data = data,
                Format = "pdf",
                ResponseType = "binary"
            };

            return await GenerateBinaryAsync(payload, cancellationToken);
        }

        public async Task<byte[]> GeneratePdfAsync(ReportDocument document, object? data = null, CancellationToken cancellationToken = default)
        {
            return await GeneratePdfAsync(document.Build(), data, cancellationToken);
        }

        public async Task<byte[]> GeneratePdfFromTemplateAsync(string templateIdOrName, object? data = null, CancellationToken cancellationToken = default)
        {
            var payload = new ReportPayload
            {
                Template = templateIdOrName,
                Data = data,
                Format = "pdf",
                ResponseType = "binary"
            };

            return await GenerateBinaryAsync(payload, cancellationToken);
        }

        public async Task<byte[]> GenerateBinaryAsync(ReportPayload payload, CancellationToken cancellationToken = default)
        {
            payload.ResponseType = "binary";
            string json = JsonSerializer.Serialize(payload, JsonOptions);
            using var content = new StringContent(json, Encoding.UTF8, "application/json");
            using var request = CreateRequest(HttpMethod.Post, "/api/v1/reports/generate/", content);

            using var response = await _httpClient.SendAsync(request, cancellationToken);
            if (!response.IsSuccessStatusCode)
            {
                string errorBody = await response.Content.ReadAsStringAsync(cancellationToken);
                throw new FlowPdfApiException($"FlowPDF generation failed with HTTP {(int)response.StatusCode}: {errorBody}", (int)response.StatusCode, errorBody);
            }

            return await response.Content.ReadAsByteArrayAsync(cancellationToken);
        }

        public async Task<ReportJobResponse> CreateJobAsync(ReportPayload payload, CancellationToken cancellationToken = default)
        {
            payload.ResponseType = "json";
            string json = JsonSerializer.Serialize(payload, JsonOptions);
            using var content = new StringContent(json, Encoding.UTF8, "application/json");
            using var request = CreateRequest(HttpMethod.Post, "/api/v1/reports/generate/", content);

            using var response = await _httpClient.SendAsync(request, cancellationToken);
            string responseBody = await response.Content.ReadAsStringAsync(cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                throw new FlowPdfApiException($"Job submission failed with HTTP {(int)response.StatusCode}: {responseBody}", (int)response.StatusCode, responseBody);
            }

            return JsonSerializer.Deserialize<ReportJobResponse>(responseBody, JsonOptions)
                   ?? throw new InvalidOperationException("Failed to deserialize response from FlowPDF.");
        }

        public async Task<ReportJobResponse> GetJobStatusAsync(string jobId, CancellationToken cancellationToken = default)
        {
            using var request = CreateRequest(HttpMethod.Get, $"/api/v1/reports/{jobId}/");
            using var response = await _httpClient.SendAsync(request, cancellationToken);
            string responseBody = await response.Content.ReadAsStringAsync(cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                throw new FlowPdfApiException($"Error retrieving job {jobId}: {responseBody}", (int)response.StatusCode, responseBody);
            }

            return JsonSerializer.Deserialize<ReportJobResponse>(responseBody, JsonOptions)
                   ?? throw new InvalidOperationException("Failed to deserialize response from FlowPDF.");
        }

        public async Task<byte[]> DownloadReportAsync(string downloadUrl, CancellationToken cancellationToken = default)
        {
            string url = downloadUrl.StartsWith("http", StringComparison.OrdinalIgnoreCase)
                ? downloadUrl
                : $"{_baseUrl}{downloadUrl}";

            using var request = new HttpRequestMessage(HttpMethod.Get, url);
            request.Headers.Add("X-API-Key", _apiKey);

            using var response = await _httpClient.SendAsync(request, cancellationToken);
            if (!response.IsSuccessStatusCode)
            {
                string error = await response.Content.ReadAsStringAsync(cancellationToken);
                throw new FlowPdfApiException($"Failed to download report from {url}: {error}", (int)response.StatusCode, error);
            }

            return await response.Content.ReadAsByteArrayAsync(cancellationToken);
        }

        public async Task<byte[]> WaitForJobAndDownloadAsync(
            string jobId,
            TimeSpan? pollInterval = null,
            TimeSpan? timeout = null,
            CancellationToken cancellationToken = default)
        {
            var interval = pollInterval ?? TimeSpan.FromMilliseconds(500);
            var maxWait = timeout ?? TimeSpan.FromSeconds(60);
            var start = DateTime.UtcNow;

            while (DateTime.UtcNow - start < maxWait)
            {
                var status = await GetJobStatusAsync(jobId, cancellationToken);
                if (status.Status == "completed")
                {
                    if (string.IsNullOrEmpty(status.DownloadUrl))
                        throw new InvalidOperationException("Report completed but download_url is null.");
                    return await DownloadReportAsync(status.DownloadUrl, cancellationToken);
                }
                if (status.Status == "failed")
                {
                    throw new FlowPdfApiException($"Report generation failed: {status.ErrorMessage}", 500, status.ErrorMessage);
                }

                await Task.Delay(interval, cancellationToken);
            }

            throw new TimeoutException($"Timeout waiting for report job {jobId} to complete.");
        }

        public void Dispose()
        {
            if (_ownsHttpClient)
            {
                _httpClient.Dispose();
            }
        }
    }

    public class FlowPdfApiException : Exception
    {
        public int StatusCode { get; }
        public string? ResponseBody { get; }

        public FlowPdfApiException(string message, int statusCode, string? responseBody) : base(message)
        {
            StatusCode = statusCode;
            ResponseBody = responseBody;
        }
    }
}
