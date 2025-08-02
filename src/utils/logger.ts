/**
 * Logger Utility
 * Provides structured logging for the LeaseWatch application
 */

export enum LogLevel {
  ERROR = 0,
  WARN = 1,
  INFO = 2,
  DEBUG = 3
}

export class Logger {
  private level: LogLevel;

  constructor(level: LogLevel = LogLevel.INFO) {
    this.level = level;
  }

  error(message: string, error?: Error): void {
    if (this.level >= LogLevel.ERROR) {
      const timestamp = new Date().toISOString();
      console.error(`[${timestamp}] ❌ ERROR: ${message}`);
      if (error) {
        console.error(`Stack trace: ${error.stack}`);
      }
    }
  }

  warn(message: string): void {
    if (this.level >= LogLevel.WARN) {
      const timestamp = new Date().toISOString();
      console.warn(`[${timestamp}] ⚠️  WARN: ${message}`);
    }
  }

  info(message: string): void {
    if (this.level >= LogLevel.INFO) {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] ℹ️  INFO: ${message}`);
    }
  }

  debug(message: string): void {
    if (this.level >= LogLevel.DEBUG) {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] 🐛 DEBUG: ${message}`);
    }
  }

  success(message: string): void {
    if (this.level >= LogLevel.INFO) {
      const timestamp = new Date().toISOString();
      console.log(`[${timestamp}] ✅ SUCCESS: ${message}`);
    }
  }

  setLevel(level: LogLevel): void {
    this.level = level;
  }
}

// Export a default logger instance
export const logger = new Logger();
