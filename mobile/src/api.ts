import { API_BASE_URL } from "./config";

export type HealthResponse = {
  status: string;
  service: string;
};

export type Account = {
  id: string;
  name: string;
  type: string;
  balance: number;
  currency: string;
};

export type PaymentResponse = {
  payment_id: string;
  status: string;
  message: string;
};

async function requestJson<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      "x-request-id": `mobile-demo-${Date.now()}`,
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API request failed: ${response.status} ${body}`);
  }

  return response.json() as Promise<T>;
}

export function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/health");
}

export function getAccounts(): Promise<Account[]> {
  return requestJson<Account[]>("/accounts");
}

export function createDemoPayment(): Promise<PaymentResponse> {
  return requestJson<PaymentResponse>("/payments", {
    method: "POST",
    body: JSON.stringify({
      from_account_id: "demo-chequing-001",
      to_payee: "Demo Utility",
      amount: 25.5,
      currency: "CAD",
    }),
  });
}

