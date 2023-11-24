import { Injectable } from '@nestjs/common';
import * as grade from 'vocabulary-level-grader';
import { AnalyzeCEFRDto } from './analyze-cefr.dto';
import { CEFREvaluationDto } from './cefr-evaluation.dto';

@Injectable()
export class CEFRService {
  analyzeCEFR(analyzeCEFRDto: AnalyzeCEFRDto): CEFREvaluationDto {
    const contentToEvaluate = analyzeCEFRDto.content;
    const evaluation: CEFREvaluationDto = grade(contentToEvaluate);
    return evaluation;
  }
}
