import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { CEFRController } from './cefr/cefr.controller';
import { CEFRService } from './cefr/cefr.service';

@Module({
  imports: [],
  controllers: [AppController, CEFRController],
  providers: [AppService, CEFRService],
})
export class AppModule {}
