/**
 * Storage Service
 * Handles data persistence for apartment pricing data
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import { DailyReport, ScrapingResult } from '../types/types';

export class StorageService {
  private readonly dataDir: string;
  private readonly pricesFile: string;

  constructor(dataDir: string = path.join(process.cwd(), 'data')) {
    this.dataDir = dataDir;
    this.pricesFile = path.join(dataDir, 'prices.json');
  }

  async ensureDataDirectory(): Promise<void> {
    try {
      await fs.access(this.dataDir);
    } catch {
      await fs.mkdir(this.dataDir, { recursive: true });
    }
  }

  async saveDailyReport(report: DailyReport): Promise<void> {
    await this.ensureDataDirectory();
    
    try {
      const reportData = JSON.stringify(report, null, 2);
      await fs.writeFile(this.pricesFile, reportData, 'utf8');
      console.log(`💾 Daily report saved to ${this.pricesFile}`);
    } catch (error) {
      console.error('❌ Error saving daily report:', error);
      throw error;
    }
  }

  async loadDailyReport(): Promise<DailyReport | null> {
    try {
      const data = await fs.readFile(this.pricesFile, 'utf8');
      return JSON.parse(data) as DailyReport;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        return null; // File doesn't exist
      }
      console.error('❌ Error loading daily report:', error);
      throw error;
    }
  }

  async saveScrapingResult(result: ScrapingResult): Promise<void> {
    await this.ensureDataDirectory();
    
    const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const filename = `${result.source.toLowerCase().replace(/\s+/g, '-')}-${timestamp}.json`;
    const filepath = path.join(this.dataDir, filename);
    
    try {
      const resultData = JSON.stringify(result, null, 2);
      await fs.writeFile(filepath, resultData, 'utf8');
      console.log(`💾 Scraping result saved to ${filepath}`);
    } catch (error) {
      console.error('❌ Error saving scraping result:', error);
      throw error;
    }
  }
}
