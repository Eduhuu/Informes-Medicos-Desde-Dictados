import { Pressable, StyleSheet, Text, View } from 'react-native';

import { UI_MODE_FILE, UI_MODE_MICROPHONE } from '../constants/UiStrings';

export const SCREEN_MODE_MICROPHONE = 'microphone';
export const SCREEN_MODE_FILE = 'file';

const MODES = [
  { key: SCREEN_MODE_MICROPHONE, label: UI_MODE_MICROPHONE },
  { key: SCREEN_MODE_FILE, label: UI_MODE_FILE },
];

export function ModeSelector({ mode, onModeChange }) {
  return (
    <View style={styles.container}>
      {MODES.map(({ key, label }) => {
        const isActive = mode === key;

        return (
          <Pressable
            key={key}
            style={[styles.tab, isActive && styles.tabActive]}
            onPress={() => onModeChange(key)}
          >
            <Text style={[styles.tabText, isActive && styles.tabTextActive]}>
              {label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: '#F1F5F9',
    borderRadius: 12,
    padding: 4,
    gap: 4,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
  },
  tabActive: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 2,
    elevation: 2,
  },
  tabText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },
  tabTextActive: {
    color: '#1D4ED8',
  },
});
