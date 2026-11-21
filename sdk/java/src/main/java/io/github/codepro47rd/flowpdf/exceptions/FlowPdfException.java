package io.github.codepro47rd.flowpdf.exceptions;

public class FlowPdfException extends RuntimeException {
    public FlowPdfException(String message) {
        super(message);
    }

    public FlowPdfException(String message, Throwable cause) {
        super(message, cause);
    }
}
