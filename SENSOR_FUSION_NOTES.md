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
