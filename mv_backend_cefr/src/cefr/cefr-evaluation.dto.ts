export class CEFREvaluationDto {
  meta: {
    words: number;
    grade: 'Pre-A1' | 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2';
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
