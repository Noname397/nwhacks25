import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet } from "react-native";

type Route = {
  mode: string;
  duration: string;
  duration_value: number;
  steps: string | string[];
};

const App = () => {
  const [routes, setRoutes] = useState<Route[]>([]);

  useEffect(() => {
    // Replace with your backend URL
    const fetchRoutes = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/map/fastest-route", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            origin: "5610 Kullahun Drive",
            destination: "UBC Bus Loop",
          }),
        });
        const data = await response.json();
        if (data.status === "success") {
          setRoutes(data.routes);
        } else {
          console.error("Failed to fetch routes:", data.error);
        }
      } catch (error) {
        console.error("Error fetching routes:", error);
      }
    };

    fetchRoutes();
  }, []);

  return (
    <View style={styles.container}>
      {/* Iterate through routes */}
      {routes.map((route, index) => (
        <View key={index} style={styles.infoRow}>
          <Text style={styles.icon}>
            {route.mode === "driving" ? "🚗" : route.mode === "walking" ? "🚶" : "🚌"}
          </Text>
          <View style={styles.infoTextContainer}>
            <Text style={styles.route}>{route.steps}</Text>
          </View>
          <Text style={styles.duration}>{route.duration}</Text>
        </View>
      ))}
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
  route: {
    color: "#555",
    fontSize: 14,
  },
  duration: {
    fontWeight: "bold",
    fontSize: 16,
    color: "#333",
  },
});

export default App;
