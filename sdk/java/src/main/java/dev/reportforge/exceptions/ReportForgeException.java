package dev.reportforge.exceptions;

public class ReportForgeException extends RuntimeException {
    public ReportForgeException(String message) {
        super(message);
    }

    public ReportForgeException(String message, Throwable cause) {
        super(message, cause);
    }
}
