import React from "react";
import { View, Text, StyleSheet, Image } from "react-native";
import { CountdownCircleTimer } from "react-native-countdown-circle-timer";

const App = () => {
  return (
    <View style={styles.container}>
      {/* Card */}
      <View style={styles.card}>
        
      </View>

      {/* Three Smaller Bars */}
      <View style={styles.infoContainer}>
        {/* Bus Row */}
        <View style={styles.infoRow}>
          <Text style={styles.icon}>🚌</Text>
          <View style={styles.infoTextContainer}>
            <Text style={styles.timeRange}>17:01 - 17:19</Text>
            <Text style={styles.route}>084 ➔ Walk</Text>
          </View>
          <Text style={styles.duration}>18 mins</Text>
        </View>

        {/* Walk Row */}
        <View style={styles.infoRow}>
          <Text style={styles.icon}>🚶</Text>
          <View style={styles.infoTextContainer}>
            <Text style={styles.timeRange}>17:01 - 17:45</Text>
            <Text style={styles.route}>via Spanish Trail (23)</Text>
          </View>
          <Text style={styles.duration}>44 mins</Text>
        </View>

        {/* Car Row */}
        <View style={styles.infoRow}>
          <Text style={styles.icon}>🚗</Text>
          <View style={styles.infoTextContainer}>
            <Text style={styles.timeRange}>17:01 - 17:05</Text>
            <Text style={styles.route}>via Chancellor Blvd E</Text>
          </View>
          <Text style={styles.duration}>4 mins</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#EDEBFF",
    justifyContent: "center",
    alignItems: "center",
  },
  card: {
    width: 350,
    height: 350,
    bottom: 70,
    backgroundColor: "white",
    borderRadius: 50,
    alignItems: "center",
    justifyContent: "flex-start",
    padding: 40,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    elevation: 5,
    marginBottom: 20, // Add spacing below the card
  },
  timer:{ 
    bottom: 100

  },
  
  infoContainer: {
    width: 350,
    bottom: 50,
    alignItems: "center",
  },
  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "white",
    padding: 15,
    borderRadius: 30,
    width: "100%",
    marginBottom: 30,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    elevation: 5,
  },
  icon: {
    fontSize: 24,
    marginRight: 10,
  },
  infoTextContainer: {
    flex: 1,
  },
  timeRange: {
    fontWeight: "bold",
    fontSize: 16,
  },
  route: {
    color: "#555",
    fontSize: 14,
  },
  trafficInfo: {
    color: "#999",
    fontSize: 12,
  },
  duration: {
    fontWeight: "bold",
    fontSize: 16,
    color: "#333",
  },
});

export default App;
