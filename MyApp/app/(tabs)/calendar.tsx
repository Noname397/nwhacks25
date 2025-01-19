import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

const ScheduleScreen = () => {
  const scheduleItems = [
    { time: '12:00', title: 'CPSC213', location: 'Life Sciences Building', duration: '12:00PM - 01:00PM' },
    { time: '13:00', title: 'CPSC221', location: 'Life Sciences Building', duration: '01:00PM - 02:00PM' },
    { time: '14:00', title: 'MATH200', location: 'Life Sciences Building', duration: '02:00PM - 03:00PM' },
    { time: '16:00', title: 'STAT251', location: 'Life Sciences Building', duration: '04:00PM - 05:00PM' },
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Schedule</Text>
      <View style={styles.purpleBox}>
        <ScrollView contentContainerStyle={styles.scrollView}>
          {scheduleItems.map((item, index) => (
            <View style={styles.scheduleItem} key={index}>
              <View style={styles.timeBox}>
                <Text style={styles.timeText}>{item.time}</Text>
              </View>
              <View style={styles.details}>
                <Text style={styles.title}>{item.title}</Text>
                <Text style={styles.location}>{item.location}</Text>
                <Text style={styles.duration}>{item.duration}</Text>
              </View>
            </View>
          ))}
        </ScrollView>
        <TouchableOpacity style={styles.importButton}>
          <Text style={styles.importButtonText}>Import</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#E8E8FC',
    padding: 20,
    paddingTop: 40,
    alignItems: 'center'
  },
  header: {
    top: 60,
    width: '60%',
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFF',
    backgroundColor: '#A5A5F8',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    overflow: 'hidden',
    marginBottom: 20,
    textAlign: 'center',
  },
  purpleBox: {
    backgroundColor: '#A5A5F8', // Same color as the schedule header
    borderRadius: 20,
    padding: 20,
    flex: 1,
    maxHeight: 550,
    top: 70,
    width: '100%', // Ensure it takes full width
  },
  scrollView: {
    width: '100%',
    flexGrow: 1,
  },
  scheduleItem: {
    flexDirection: 'row', // Align items in a row
    backgroundColor: '#FFF',
    borderRadius: 15,
    padding: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 3,
  },
  timeBox: {
    width: 60, // Fixed width to make it square
    height: 60, // Fixed height to make it square
    borderRadius: 15,
    backgroundColor: '#A5A5F8',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
  },
  timeText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFF',
  },
  details: {
    flex: 1,
    justifyContent: 'center',
  },
  title: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000',
    marginBottom: 5,
  },

  location: {
    fontSize: 14,
    color: '#555',
    marginBottom: 5,
  },
  duration: {
    fontSize: 12,
    color: '#888',
  },
  importButton: {
    marginTop: 20,
    backgroundColor: '#6B6BF0',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 3,
    alignSelf: 'center',
  },
  importButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFF',
  },
});

export default ScheduleScreen;