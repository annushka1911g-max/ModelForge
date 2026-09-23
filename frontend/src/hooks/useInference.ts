import { useState } from 'react';

export const useInference = () => {
  const [prediction] = useState<any>(null);
  const [loading] = useState<boolean>(false);
  const [error] = useState<string | null>(null);

  return { prediction, loading, error };
};
