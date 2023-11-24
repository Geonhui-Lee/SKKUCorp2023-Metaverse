import { Body, Controller, Post } from '@nestjs/common';
import { CEFRService } from './cefr.service';
import { AnalyzeCEFRDto } from './analyze-cefr.dto';
import { CEFREvaluationDto } from './cefr-evaluation.dto';

@Controller()
export class CEFRController {
  constructor(private readonly appService: CEFRService) {}

  @Post('analyze/cefr')
  analyzeCEFR(@Body() analyzeCEFRDto: AnalyzeCEFRDto): CEFREvaluationDto {
    return this.appService.analyzeCEFR(analyzeCEFRDto);
  }
}
