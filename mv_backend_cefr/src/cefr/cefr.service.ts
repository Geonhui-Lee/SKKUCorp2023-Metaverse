import { Injectable } from '@nestjs/common';
import * as grade from 'vocabulary-level-grader';
import { AnalyzeCEFRDto } from './analyze-cefr.dto';
import { CEFREvaluationDto } from './cefr-evaluation.dto';

@Injectable()
export class CEFRService {
  analyzeCEFR(analyzeCEFRDto: AnalyzeCEFRDto): CEFREvaluationDto {
    const contentToEvaluate = analyzeCEFRDto.content;
    const evaluation: CEFREvaluationDto = grade(contentToEvaluate);

    // Get normalized level value
    function getNormalizedLevelValue(level: number): number {
      return level >= 100 ? 0 : level;
    }

    // CEFR level dictionary (normalized value)
    const levels = {
      A1: getNormalizedLevelValue(evaluation.meta.levels.A1),
      A2: getNormalizedLevelValue(evaluation.meta.levels.A2),
      B1: getNormalizedLevelValue(evaluation.meta.levels.B1),
      B2: getNormalizedLevelValue(evaluation.meta.levels.B2),
      C1: getNormalizedLevelValue(evaluation.meta.levels.C1),
      C2: getNormalizedLevelValue(evaluation.meta.levels.C2),
    };
    evaluation.meta.levels = levels;
    
    const normalizedGrade = [];
    for (const level in levels) {
      if (levels[level] >= 90 && levels[level] < 100) {
        normalizedGrade.push(level);
        break;
      }
    }
    if (
      (levels.A1 > 0 || levels.A2 > 0) &&
      levels.B1 == 0 &&
      levels.B2 == 0 &&
      levels.C1 == 0 &&
      levels.C2 == 0
    ) {
      normalizedGrade.push('Pre-A1');
    }
    if (normalizedGrade.length == 0) {
      // get the level with the highest value
      let highestLevel = 'N/A';
      let highestLevelValue = 0;
      for (const level in levels) {
        if (levels[level] > highestLevelValue) {
          highestLevelValue = levels[level];
          highestLevel = level;
        }
      }
      normalizedGrade.push(highestLevel);
    }

    // Update the grade evaluation with the normalized value
    evaluation.meta.grade = normalizedGrade[
      normalizedGrade.length - 1
    ] as CEFREvaluationDto['meta']['grade'];

    return evaluation;
  }
}
