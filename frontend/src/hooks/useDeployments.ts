import { useState } from 'react';
import { Deployment } from '../types';

export const useDeployments = () => {
  const [deployments] = useState<Deployment[]>([]);
  const [loading] = useState<boolean>(false);
  const [error] = useState<string | null>(null);

  return { deployments, loading, error };
};
