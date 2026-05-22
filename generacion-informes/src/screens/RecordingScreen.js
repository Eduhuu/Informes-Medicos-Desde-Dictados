import { useMemo } from 'react';
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';

import {
  UI_CHUNKS_EMITTED,
  UI_ENERGY_LEVEL,
  UI_ERROR_GENERIC,
  UI_ERROR_MICROPHONE,
  UI_LAST_CHUNK_DURATION,
  UI_LISTENING,
  UI_MS_SUFFIX,
  UI_PAUSE_DETECTED,
  UI_PERMISSION_DENIED,
  UI_PERMISSION_GRANTED,
  UI_PERMISSION_PENDING,
  UI_RECORDING_ACTIVE,
  UI_RECORDING_IDLE,
  UI_SECONDS_SUFFIX,
  UI_SESSION_DURATION,
  UI_SILENCE,
  UI_START_RECORDING,
  UI_STOP_RECORDING,
  UI_TITLE,
  UI_WS_CONNECTED,
  UI_WS_CONNECTING,
  UI_WS_DISCONNECTED,
  UI_WS_ERROR,
} from '../constants/UiStrings';
import { useAudioCaptureSession } from '../hooks/useAudioCaptureSession';

function formatDuration(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function ConnectionBadge({ state }) {
  const label = useMemo(() => {
    switch (state) {
      case 'connected':
        return UI_WS_CONNECTED;
      case 'connecting':
        return UI_WS_CONNECTING;
      case 'error':
        return UI_WS_ERROR;
      default:
        return UI_WS_DISCONNECTED;
    }
  }, [state]);

  return (
    <View style={[styles.badge, styles[`badge_${state}`]]}>
      <Text style={styles.badgeText}>{label}</Text>
    </View>
  );
}

function PermissionStatus({ status }) {
  const label = useMemo(() => {
    switch (status) {
      case 'granted':
        return UI_PERMISSION_GRANTED;
      case 'denied':
        return UI_PERMISSION_DENIED;
      default:
        return UI_PERMISSION_PENDING;
    }
  }, [status]);

  return <Text style={styles.permissionText}>{label}</Text>;
}

export default function RecordingScreen() {
  const {
    permissionStatus,
    isRecording,
    connectionState,
    chunksEmitted,
    lastChunkDurationMs,
    sessionDurationSec,
    energyLevel,
    isSpeaking,
    errorMessage,
    startSession,
    stopSession,
  } = useAudioCaptureSession();

  const activityLabel = isRecording
    ? isSpeaking
      ? UI_LISTENING
      : UI_PAUSE_DETECTED
    : UI_SILENCE;

  const recordingLabel = isRecording ? UI_RECORDING_ACTIVE : UI_RECORDING_IDLE;
  const energyPercent = Math.min(Math.round(energyLevel * 1000), 100);

  const handlePrimaryAction = () => {
    if (isRecording) {
      stopSession();
      return;
    }

    startSession();
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <Text style={styles.title}>{UI_TITLE}</Text>

      <View style={styles.card}>
        <Text style={styles.sectionLabel}>{recordingLabel}</Text>
        <ConnectionBadge state={connectionState} />
        <PermissionStatus status={permissionStatus} />
      </View>

      <View style={styles.card}>
        <Text style={styles.activityLabel}>{activityLabel}</Text>
        <View style={styles.energyTrack}>
          <View style={[styles.energyFill, { width: `${energyPercent}%` }]} />
        </View>
        <Text style={styles.metricText}>
          {UI_ENERGY_LEVEL}: {energyPercent}%
        </Text>
      </View>

      <View style={styles.metricsGrid}>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>{UI_SESSION_DURATION}</Text>
          <Text style={styles.metricValue}>
            {formatDuration(sessionDurationSec)}
            {UI_SECONDS_SUFFIX}
          </Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>{UI_CHUNKS_EMITTED}</Text>
          <Text style={styles.metricValue}>{chunksEmitted}</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>{UI_LAST_CHUNK_DURATION}</Text>
          <Text style={styles.metricValue}>
            {lastChunkDurationMs}
            {UI_MS_SUFFIX}
          </Text>
        </View>
      </View>

      {permissionStatus === 'pending' && isRecording ? (
        <ActivityIndicator size="large" color="#1D4ED8" />
      ) : null}

      {errorMessage ? (
        <Text style={styles.errorText}>
          {errorMessage === 'No se pudo acceder al micrófono'
            ? UI_ERROR_MICROPHONE
            : UI_ERROR_GENERIC}
        </Text>
      ) : null}

      <Pressable
        style={[
          styles.primaryButton,
          isRecording ? styles.stopButton : styles.startButton,
        ]}
        onPress={handlePrimaryAction}
      >
        <Text style={styles.primaryButtonText}>
          {isRecording ? UI_STOP_RECORDING : UI_START_RECORDING}
        </Text>
      </Pressable>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    paddingHorizontal: 20,
    paddingTop: 16,
    gap: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#0F172A',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    gap: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  sectionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#334155',
  },
  permissionText: {
    fontSize: 14,
    color: '#64748B',
  },
  activityLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#0F172A',
  },
  energyTrack: {
    height: 12,
    borderRadius: 999,
    backgroundColor: '#E2E8F0',
    overflow: 'hidden',
  },
  energyFill: {
    height: '100%',
    backgroundColor: '#2563EB',
  },
  metricText: {
    fontSize: 14,
    color: '#475569',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  metricCard: {
    flexGrow: 1,
    minWidth: '30%',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  metricLabel: {
    fontSize: 13,
    color: '#64748B',
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#0F172A',
  },
  primaryButton: {
    marginTop: 'auto',
    marginBottom: 24,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
  },
  startButton: {
    backgroundColor: '#2563EB',
  },
  stopButton: {
    backgroundColor: '#DC2626',
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  badge: {
    alignSelf: 'flex-start',
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  badge_disconnected: {
    backgroundColor: '#E2E8F0',
  },
  badge_connecting: {
    backgroundColor: '#FEF3C7',
  },
  badge_connected: {
    backgroundColor: '#DCFCE7',
  },
  badge_error: {
    backgroundColor: '#FEE2E2',
  },
  badgeText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#0F172A',
  },
  errorText: {
    color: '#B91C1C',
    fontSize: 14,
  },
});
