import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import {
  UI_FILE_LIST_EMPTY,
  UI_FILE_STATUS_ERROR,
  UI_FILE_STATUS_IDLE,
  UI_FILE_STATUS_SENDING,
  UI_FILE_STATUS_SENT,
  UI_REMOVE_FILE,
  UI_SEND_FILE,
} from '../constants/UiStrings';
import {
  FILE_STATUS_ERROR,
  FILE_STATUS_IDLE,
  FILE_STATUS_SENDING,
  FILE_STATUS_SENT,
} from '../hooks/useAudioFileSession';

const STATUS_LABELS = {
  [FILE_STATUS_IDLE]: UI_FILE_STATUS_IDLE,
  [FILE_STATUS_SENDING]: UI_FILE_STATUS_SENDING,
  [FILE_STATUS_SENT]: UI_FILE_STATUS_SENT,
  [FILE_STATUS_ERROR]: UI_FILE_STATUS_ERROR,
};

const KB = 1024;

function formatSize(bytes) {
  if (bytes === 0) {
    return '—';
  }

  return `${Math.round(bytes / KB)} KB`;
}

function StatusBadge({ status }) {
  return (
    <View style={[styles.badge, styles[`badge_${status}`]]}>
      <Text style={[styles.badgeText, styles[`badgeText_${status}`]]}>
        {STATUS_LABELS[status] ?? status}
      </Text>
    </View>
  );
}

function FileRow({ file, onSend, onRemove, isSending }) {
  const canSend = file.status === FILE_STATUS_IDLE || file.status === FILE_STATUS_ERROR;

  return (
    <View style={styles.row}>
      <View style={styles.rowInfo}>
        <Text style={styles.fileName} numberOfLines={1}>
          {file.name}
        </Text>
        <Text style={styles.fileMeta}>{formatSize(file.sizeBytes)}</Text>
        {file.errorMessage ? (
          <Text style={styles.errorText} numberOfLines={2}>
            {file.errorMessage}
          </Text>
        ) : null}
      </View>

      <View style={styles.rowRight}>
        <StatusBadge status={file.status} />

        <View style={styles.rowActions}>
          <Pressable
            style={[styles.actionButton, styles.sendButton, (!canSend || isSending) && styles.buttonDisabled]}
            onPress={() => onSend(file.id)}
            disabled={!canSend || isSending}
          >
            <Text style={styles.sendButtonText}>{UI_SEND_FILE}</Text>
          </Pressable>

          <Pressable
            style={[styles.actionButton, styles.removeButton]}
            onPress={() => onRemove(file.id)}
            disabled={file.status === FILE_STATUS_SENDING}
          >
            <Text style={styles.removeButtonText}>{UI_REMOVE_FILE}</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

export function AudioFileList({ files, onSend, onRemove, isSending }) {
  if (files.length === 0) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>{UI_FILE_LIST_EMPTY}</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.list} contentContainerStyle={styles.listContent}>
      {files.map((file) => (
        <FileRow
          key={file.id}
          file={file}
          onSend={onSend}
          onRemove={onRemove}
          isSending={isSending}
        />
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  list: {
    flex: 1,
  },
  listContent: {
    gap: 10,
    paddingBottom: 16,
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 24,
    paddingVertical: 32,
  },
  emptyText: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
    lineHeight: 22,
  },
  row: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  rowInfo: {
    flex: 1,
    gap: 4,
  },
  fileName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#0F172A',
  },
  fileMeta: {
    fontSize: 12,
    color: '#94A3B8',
  },
  errorText: {
    fontSize: 12,
    color: '#B91C1C',
    marginTop: 2,
  },
  rowRight: {
    alignItems: 'flex-end',
    gap: 8,
  },
  rowActions: {
    flexDirection: 'row',
    gap: 6,
  },
  badge: {
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  badge_idle: { backgroundColor: '#F1F5F9' },
  badge_sending: { backgroundColor: '#FEF3C7' },
  badge_sent: { backgroundColor: '#DCFCE7' },
  badge_error: { backgroundColor: '#FEE2E2' },
  badgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  badgeText_idle: { color: '#475569' },
  badgeText_sending: { color: '#92400E' },
  badgeText_sent: { color: '#166534' },
  badgeText_error: { color: '#991B1B' },
  actionButton: {
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  sendButton: {
    backgroundColor: '#2563EB',
  },
  removeButton: {
    backgroundColor: '#F1F5F9',
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  buttonDisabled: {
    opacity: 0.4,
  },
  sendButtonText: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '600',
  },
  removeButtonText: {
    color: '#64748B',
    fontSize: 13,
    fontWeight: '600',
  },
});
