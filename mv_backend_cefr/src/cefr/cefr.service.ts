import { Injectable } from '@nestjs/common';
import * as grade from 'vocabulary-level-grader';
import { AnalyzeCEFRDto } from './analyze-cefr.dto';
import { CEFREvaluationDto } from './cefr-evaluation.dto';

// https://github.com/openderock/vocabulary-level-grader
@Injectable()
export class CEFRService {
  analyzeCEFR(analyzeCEFRDto: AnalyzeCEFRDto): CEFREvaluationDto {
    const contentToEvaluate = analyzeCEFRDto.content;
    const evaluation: CEFREvaluationDto = grade(contentToEvaluate);

    function getNormalizedLevelValue(level: number): number {
      //return level >= 100 ? 0 : level;
      return level;
    }
    const levels = {
      A1: getNormalizedLevelValue(evaluation.meta.levels.A1),
      A2: getNormalizedLevelValue(evaluation.meta.levels.A2),
      B1: getNormalizedLevelValue(evaluation.meta.levels.B1),
      B2: getNormalizedLevelValue(evaluation.meta.levels.B2),
      C1: getNormalizedLevelValue(evaluation.meta.levels.C1),
      C2: getNormalizedLevelValue(evaluation.meta.levels.C2),
    };
    evaluation.meta.levels = levels;

    const normalizedGrade = ['IDK'];
    for (const level in levels) {
      if (levels[level] >= 90) {
        normalizedGrade.push(level);
        break;
      }
    }
    evaluation.meta.grade = normalizedGrade[
      normalizedGrade.length - 1
    ] as CEFREvaluationDto['meta']['grade'];

    return evaluation;
  }
}
