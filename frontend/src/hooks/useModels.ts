import { useState } from 'react';
import { Model } from '../types';

export const useModels = () => {
  const [models] = useState<Model[]>([]);
  const [loading] = useState<boolean>(false);
  const [error] = useState<string | null>(null);

  // Hook skeleton: feature implementation in later phase
  return { models, loading, error };
};
