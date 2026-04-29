import { StatusBar } from 'expo-status-bar';
import { useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { API_BASE_URL } from './src/config';
import {
  Account,
  createDemoPayment,
  getAccounts,
  getHealth,
  HealthResponse,
  PaymentResponse,
} from './src/api';

type RequestState = 'idle' | 'loading' | 'success' | 'error';

export default function App() {
  const [requestState, setRequestState] = useState<RequestState>('idle');
  const [message, setMessage] = useState('Choose an action to call the demo API.');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [payment, setPayment] = useState<PaymentResponse | null>(null);

  async function runAction(action: () => Promise<void>) {
    setRequestState('loading');
    setMessage('Calling API...');

    try {
      await action();
      setRequestState('success');
    } catch (error) {
      setRequestState('error');
      setMessage(error instanceof Error ? error.message : 'Unknown API error');
    }
  }

  function resetResults() {
    setHealth(null);
    setAccounts([]);
    setPayment(null);
  }

  function handleHealthCheck() {
    runAction(async () => {
      resetResults();
      const result = await getHealth();
      setHealth(result);
      setMessage(`Health check returned ${result.status}.`);
    });
  }

  function handleFetchAccounts() {
    runAction(async () => {
      resetResults();
      const result = await getAccounts();
      setAccounts(result);
      setMessage(`Fetched ${result.length} demo accounts.`);
    });
  }

  function handleDemoPayment() {
    runAction(async () => {
      resetResults();
      const result = await createDemoPayment();
      setPayment(result);
      setMessage(result.message);
    });
  }

  return (
    <SafeAreaView style={styles.screen}>
      <StatusBar style="auto" />
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.eyebrow}>Mobile Platform Reliability Lab</Text>
          <Text style={styles.title}>Demo Mobile Client</Text>
          <Text style={styles.subtitle}>
            Expo TypeScript app calling the FastAPI backend through an environment-based URL.
          </Text>
        </View>

        <View style={styles.panel}>
          <Text style={styles.label}>API base URL</Text>
          <Text style={styles.mono}>{API_BASE_URL}</Text>
        </View>

        <View style={styles.actions}>
          <ActionButton title="API health check" onPress={handleHealthCheck} disabled={requestState === 'loading'} />
          <ActionButton title="Fetch accounts" onPress={handleFetchAccounts} disabled={requestState === 'loading'} />
          <ActionButton title="Make demo payment" onPress={handleDemoPayment} disabled={requestState === 'loading'} />
        </View>

        <View style={[styles.statusPanel, styles[requestState]]}>
          <View style={styles.statusHeader}>
            <Text style={styles.statusTitle}>{requestState.toUpperCase()}</Text>
            {requestState === 'loading' ? <ActivityIndicator /> : null}
          </View>
          <Text style={styles.statusMessage}>{message}</Text>
        </View>

        {health ? (
          <View style={styles.resultPanel}>
            <Text style={styles.resultTitle}>Health</Text>
            <Text style={styles.resultText}>Status: {health.status}</Text>
            <Text style={styles.resultText}>Service: {health.service}</Text>
          </View>
        ) : null}

        {accounts.length > 0 ? (
          <View style={styles.resultPanel}>
            <Text style={styles.resultTitle}>Accounts</Text>
            {accounts.map((account) => (
              <View key={account.id} style={styles.accountRow}>
                <View>
                  <Text style={styles.accountName}>{account.name}</Text>
                  <Text style={styles.accountType}>{account.type}</Text>
                </View>
                <Text style={styles.balance}>
                  {account.currency} {account.balance.toFixed(2)}
                </Text>
              </View>
            ))}
          </View>
        ) : null}

        {payment ? (
          <View style={styles.resultPanel}>
            <Text style={styles.resultTitle}>Payment</Text>
            <Text style={styles.resultText}>ID: {payment.payment_id}</Text>
            <Text style={styles.resultText}>Status: {payment.status}</Text>
          </View>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}

type ActionButtonProps = {
  title: string;
  onPress: () => void;
  disabled: boolean;
};

function ActionButton({ title, onPress, disabled }: ActionButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        pressed ? styles.buttonPressed : null,
        disabled ? styles.buttonDisabled : null,
      ]}
    >
      <Text style={styles.buttonText}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#f7f8fa',
  },
  container: {
    padding: 20,
    gap: 16,
  },
  header: {
    gap: 8,
  },
  eyebrow: {
    color: '#486284',
    fontSize: 13,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  title: {
    color: '#172033',
    fontSize: 30,
    fontWeight: '800',
  },
  subtitle: {
    color: '#56657a',
    fontSize: 16,
    lineHeight: 23,
  },
  panel: {
    backgroundColor: '#ffffff',
    borderColor: '#d9e0ea',
    borderRadius: 8,
    borderWidth: 1,
    padding: 14,
    gap: 6,
  },
  label: {
    color: '#56657a',
    fontSize: 13,
    fontWeight: '700',
  },
  mono: {
    color: '#172033',
    fontFamily: 'Courier',
    fontSize: 13,
  },
  actions: {
    gap: 10,
  },
  button: {
    alignItems: 'center',
    backgroundColor: '#1d5fd1',
    borderRadius: 8,
    minHeight: 48,
    justifyContent: 'center',
    paddingHorizontal: 16,
  },
  buttonPressed: {
    backgroundColor: '#164aa4',
  },
  buttonDisabled: {
    opacity: 0.55,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
  statusPanel: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    borderWidth: 1,
    padding: 14,
    gap: 8,
  },
  statusHeader: {
    alignItems: 'center',
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statusTitle: {
    color: '#172033',
    fontSize: 13,
    fontWeight: '800',
  },
  statusMessage: {
    color: '#334155',
    fontSize: 15,
    lineHeight: 22,
  },
  idle: {
    borderColor: '#d9e0ea',
  },
  loading: {
    borderColor: '#7aa7f7',
  },
  success: {
    borderColor: '#2d9b67',
  },
  error: {
    borderColor: '#d64545',
  },
  resultPanel: {
    backgroundColor: '#ffffff',
    borderColor: '#d9e0ea',
    borderRadius: 8,
    borderWidth: 1,
    padding: 14,
    gap: 10,
  },
  resultTitle: {
    color: '#172033',
    fontSize: 18,
    fontWeight: '800',
  },
  resultText: {
    color: '#334155',
    fontSize: 15,
  },
  accountRow: {
    alignItems: 'center',
    borderTopColor: '#eef2f6',
    borderTopWidth: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: 10,
  },
  accountName: {
    color: '#172033',
    fontSize: 15,
    fontWeight: '700',
  },
  accountType: {
    color: '#64748b',
    fontSize: 13,
    textTransform: 'capitalize',
  },
  balance: {
    color: '#172033',
    fontSize: 15,
    fontWeight: '800',
  },
});
