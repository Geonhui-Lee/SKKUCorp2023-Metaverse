export class CEFREvaluationDto {
  meta: {
    words: number;
    grade: string;
    mean: number;
    max: number;
    levels: {
      A1: number;
      A2: number;
      B1: number;
      B2: number;
      C1: number;
      C2: number;
    };
  };
  words: [string, number][];
}
