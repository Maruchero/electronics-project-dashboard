# Sensor Fusion Notes

To robustly visualize 3D orientation from a 6-axis IMU (Accelerometer + Gyroscope), we cannot use the raw data directly for rotation angles.

## The Problem
1.  **Accelerometer**: Measures all forces, including gravity.
    *   *Static:* Good for finding "Down" (Gravity vector). Can calculate **Pitch** and **Roll**.
    *   *Dynamic:* Terrible when moving. Shaking the sensor creates "fake gravity," causing the angle to jitter wildly.
    *   *Limitation:* Cannot measure **Yaw** (rotation around Z) because gravity doesn't change when you spin horizontally.
2.  **Gyroscope**: Measures angular *velocity* (degrees per second).
    *   *Method:* We must integrate this over time (Angle = Angle + Rate * dt).
    *   *Pros:* Very smooth, immune to shaking.
    *   *Cons:* **Drift**. Small errors accumulate. After 1 minute, "straight ahead" might be 20 degrees off.

## The Solution: Complementary Filter
A lightweight algorithm that combines the best of both. It trusts the Gyroscope for short-term changes (smoothness) and the Accelerometer for long-term correction (gravity reference).

### The Math
```python
# Constants
alpha = 0.98  # Trust Gyro 98%, Acc 2%
dt = 0.01     # Time between updates (seconds)

# 1. Integrate Gyro (Dead Reckoning)
pitch += gyro_x * dt
roll  += gyro_y * dt

# 2. Calculate Accelerometer Angles (Gravity Vector)
acc_pitch = atan2(acc_y, acc_z) * 180/PI
acc_roll  = atan2(-acc_x, acc_z) * 180/PI

# 3. Fuse them
pitch = alpha * pitch + (1 - alpha) * acc_pitch
roll  = alpha * roll  + (1 - alpha) * acc_roll
```

*Note: Yaw will still drift because we lack a Magnetometer (Compass).*

## Future Options (Advanced)
*   **Madgwick Filter**: Better for 6-axis, handles gimbal lock better, computationally efficient.
*   **Kalman Filter**: The "gold standard," but computationally heavy and harder to tune.

---

## Why No Double Integration for Angles?

The common misconception is that all accelerations (linear or angular) require double integration to find position or angle. This is true for **linear position** from linear acceleration. However, for **angles** derived from IMU sensors, the approach differs:

### 1. Gyroscope Outputs Angular Velocity, Not Acceleration
*   The gyroscope directly measures **angular velocity** (how fast it's rotating, e.g., in degrees/second or radians/second).
*   To get the current angle from angular velocity, you only need to perform a **single integration** over time: `Angle = Angle_Previous + (Angular_Velocity * Delta_Time)`.
*   If the gyroscope measured angular acceleration, then double integration would be required. But it doesn't.

### 2. Accelerometer Uses Gravity as an Absolute Reference for Pitch/Roll
*   For **Pitch and Roll**, the accelerometer is used to determine the direction of the **gravity vector**. Since gravity always points "down", we can use basic trigonometry (`atan2`) to calculate the tilt angles relative to this fixed reference.
*   This calculation provides an **absolute angle** that does not drift over time (unlike integrating a gyroscope). No integration is involved here; it's a direct calculation based on the current accelerometer readings.
*   The accelerometer does not measure angular acceleration. It measures linear acceleration, including the acceleration due to gravity.

### Summary of Angle Calculation for 6-Axis IMU

| Value                   | Sensor     | What it measures       | How to get Angle       | Integration |
| :---------------------- | :--------- | :--------------------- | :--------------------- | :---------- |
| **Pitch & Roll Angles** | Accelerometer | Gravity Vector (Static) | `atan2` (Trigonometry) | None        |
| **Yaw Angle**           | Gyroscope  | Angular Velocity (Rate) | Single Integration     | Single      |

This combined approach (using accelerometer for absolute Pitch/Roll, and gyroscope for relative Yaw) is the foundation of sensor fusion techniques like the Complementary Filter, providing stable and drift-free pitch and roll estimates, and a smooth (but drifting) yaw estimate.