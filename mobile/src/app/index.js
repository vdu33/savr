import { useCallback, useEffect, useState } from 'react';
import {
    ActivityIndicator,
    FlatList,
    RefreshControl,
    SafeAreaView,
    StatusBar,
    StyleSheet,
    Text,
    View,
} from 'react-native';

const API_URL = 'https://backend-api-production-6b48.up.railway.app/deals';

const CATEGORY_COLORS = {
  drinks: '#4A90D9',
  entrees: '#E8734A',
  dessert: '#C25AA3',
  brunch: '#E8A93E',
};

function formatDays(days) {
  if (!days || days.length === 0) return 'Every day';
  return days.map((d) => d[0].toUpperCase() + d.slice(1, 3)).join(', ');
}

function DealCard({ deal }) {
  const color = CATEGORY_COLORS[deal.category] || '#6B7280';
  return (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.business}>{deal.business_name}</Text>
        {deal.needs_review && (
          <View style={styles.reviewBadge}>
            <Text style={styles.reviewBadgeText}>unverified</Text>
          </View>
        )}
      </View>
      <Text style={styles.title}>{deal.title}</Text>
      {deal.description ? (
        <Text style={styles.description}>{deal.description}</Text>
      ) : null}
      <View style={styles.footer}>
        <View style={[styles.categoryPill, { backgroundColor: color }]}>
          <Text style={styles.categoryText}>
            {deal.category || deal.discount_type}
          </Text>
        </View>
        <Text style={styles.days}>{formatDays(deal.days_valid)}</Text>
      </View>
    </View>
  );
}

export default function App() {
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const fetchDeals = useCallback(async () => {
    try {
      setError(null);
      const response = await fetch(API_URL);
      if (!response.ok) throw new Error(`Server returned ${response.status}`);
      const data = await response.json();
      setDeals(data);
    } catch (err) {
      setError(
        `Couldn't load deals. Make sure the backend server is running ` +
          `and API_URL matches your computer's IP address.\n\n(${err.message})`
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchDeals();
  }, [fetchDeals]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchDeals();
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.centered}>
        <ActivityIndicator size="large" color="#E8734A" />
        <Text style={styles.loadingText}>Loading deals...</Text>
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.centered}>
        <Text style={styles.errorText}>{error}</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <View style={styles.headerBar}>
        <Text style={styles.headerTitle}>Local Bites</Text>
        <Text style={styles.headerSubtitle}>
          {deals.length} deal{deals.length !== 1 ? 's' : ''} this week
        </Text>
      </View>
      <FlatList
        data={deals}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <DealCard deal={item} />}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <Text style={styles.emptyText}>No deals found.</Text>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F3F0' },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F3F0',
    padding: 24,
  },
  loadingText: { marginTop: 12, color: '#6B7280' },
  errorText: { color: '#B4443C', textAlign: 'center', lineHeight: 20 },
  headerBar: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 16,
    backgroundColor: '#F5F3F0',
  },
  headerTitle: { fontSize: 28, fontWeight: '700', color: '#2A2A2A' },
  headerSubtitle: { fontSize: 14, color: '#6B7280', marginTop: 2 },
  list: { paddingHorizontal: 16, paddingBottom: 24 },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  business: { fontSize: 13, fontWeight: '600', color: '#8A8A8A' },
  reviewBadge: {
    backgroundColor: '#FDECEA',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  reviewBadgeText: { fontSize: 10, color: '#B4443C', fontWeight: '600' },
  title: { fontSize: 17, fontWeight: '700', color: '#2A2A2A', marginTop: 4 },
  description: { fontSize: 14, color: '#4B4B4B', marginTop: 4, lineHeight: 19 },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 12,
  },
  categoryPill: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  categoryText: { color: '#FFF', fontSize: 12, fontWeight: '600' },
  days: { fontSize: 13, color: '#8A8A8A' },
  emptyText: { textAlign: 'center', marginTop: 40, color: '#8A8A8A' },
});