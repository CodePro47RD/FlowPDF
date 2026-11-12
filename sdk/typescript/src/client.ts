import { ClientOptions, DocumentDefinition, ReportJobResponse, ReportPayload } from './types';
import { ReportDocument } from './builder';

export class ReportForgeError extends Error {
    constructor(
        message: string,
        public readonly statusCode?: number,
        public readonly responseBody?: string
    ) {
        super(message);
        this.name = 'ReportForgeError';
    }
}

export class ReportForgeClient {
    private readonly baseUrl: string;
    private readonly apiKey: string;
    private readonly timeoutMs: number;

    constructor(options: ClientOptions) {
        this.baseUrl = options.baseUrl.replace(/\/+$/, '');
        this.apiKey = options.apiKey;
        this.timeoutMs = options.timeoutMs ?? 60000;
    }

    private getHeaders(): Record<string, string> {
        return {
            'Content-Type': 'application/json',
            'X-API-Key': this.apiKey
        };
    }

    /**
     * Synchronously generates a PDF and returns the binary buffer.
     */
    async generatePdf<TData = Record<string, any>>(
        document: DocumentDefinition | ReportDocument,
        data?: TData
    ): Promise<Uint8Array> {
        const docDef = document instanceof ReportDocument ? document.build() : document;
        const payload: ReportPayload<TData> = {
            document: docDef,
            data,
            format: 'pdf',
            response_type: 'binary'
        };

        return this.generateBinary(payload);
    }

    /**
     * Synchronously generates a PDF from an existing saved template.
     */
    async generateFromTemplate<TData = Record<string, any>>(
        template: string,
        data?: TData
    ): Promise<Uint8Array> {
        const payload: ReportPayload<TData> = {
            template,
            data,
            format: 'pdf',
            response_type: 'binary'
        };

        return this.generateBinary(payload);
    }

    /**
     * Low-level binary generation endpoint call.
     */
    async generateBinary(payload: ReportPayload): Promise<Uint8Array> {
        const url = `${this.baseUrl}/api/v1/reports/generate/`;
        const body = JSON.stringify({ ...payload, response_type: 'binary' });

        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), this.timeoutMs);

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: this.getHeaders(),
                body,
                signal: controller.signal
            });

            if (!res.ok) {
                const errorText = await res.text();
                throw new ReportForgeError(
                    `Report generation failed with HTTP ${res.status}: ${errorText}`,
                    res.status,
                    errorText
                );
            }

            const arrayBuffer = await res.arrayBuffer();
            return new Uint8Array(arrayBuffer);
        } finally {
            clearTimeout(timer);
        }
    }

    /**
     * Submit an asynchronous report generation job (Celery).
     */
    async createJob(payload: ReportPayload): Promise<ReportJobResponse> {
        const url = `${this.baseUrl}/api/v1/reports/generate/`;
        const body = JSON.stringify({ ...payload, response_type: 'json' });

        const res = await fetch(url, {
            method: 'POST',
            headers: this.getHeaders(),
            body
        });

        if (!res.ok) {
            const errorText = await res.text();
            throw new ReportForgeError(
                `Failed to create report job (HTTP ${res.status}): ${errorText}`,
                res.status,
                errorText
            );
        }

        return (await res.json()) as ReportJobResponse;
    }

    /**
     * Check the status of an asynchronous job.
     */
    async getJobStatus(jobId: string): Promise<ReportJobResponse> {
        const url = `${this.baseUrl}/api/v1/reports/${jobId}/`;
        const res = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders()
        });

        if (!res.ok) {
            const errorText = await res.text();
            throw new ReportForgeError(
                `Failed to retrieve job status (HTTP ${res.status}): ${errorText}`,
                res.status,
                errorText
            );
        }

        return (await res.json()) as ReportJobResponse;
    }

    /**
     * Download completed report bytes from a download URL.
     */
    async downloadReport(downloadUrl: string): Promise<Uint8Array> {
        const fullUrl = downloadUrl.startsWith('http') ? downloadUrl : `${this.baseUrl}${downloadUrl}`;
        const res = await fetch(fullUrl, {
            method: 'GET',
            headers: this.getHeaders()
        });

        if (!res.ok) {
            const errorText = await res.text();
            throw new ReportForgeError(
                `Failed to download report from ${fullUrl} (HTTP ${res.status}): ${errorText}`,
                res.status,
                errorText
            );
        }

        const buffer = await res.arrayBuffer();
        return new Uint8Array(buffer);
    }

    /**
     * Helper to poll an async job until completion and download its binary contents.
     */
    async waitForJobAndDownload(
        jobId: string,
        options?: { pollIntervalMs?: number; timeoutMs?: number }
    ): Promise<Uint8Array> {
        const interval = options?.pollIntervalMs ?? 500;
        const maxWait = options?.timeoutMs ?? 60000;
        const start = Date.now();

        while (Date.now() - start < maxWait) {
            const status = await this.getJobStatus(jobId);
            if (status.status === 'completed') {
                if (!status.download_url) {
                    throw new ReportForgeError('Job completed without a download URL.');
                }
                return this.downloadReport(status.download_url);
            }
            if (status.status === 'failed') {
                throw new ReportForgeError(`Report job failed: ${status.error_message ?? 'Unknown error'}`);
            }

            await new Promise((r) => setTimeout(r, interval));
        }

        throw new ReportForgeError(`Timeout waiting for job ${jobId} to complete.`);
    }
}
