<picture>
  <source media="(prefers-color-scheme: dark) and (prefers-reduced-motion: reduce)" srcset="assets/workbench-dark.png">
  <source media="(prefers-color-scheme: light) and (prefers-reduced-motion: reduce)" srcset="assets/workbench-light.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/workbench-light.gif">
  <img src="assets/workbench-dark.gif" alt="Evan Girard-Sun. Robotics and embedded systems at Rice University. A small robot waves hello." width="100%">
</picture>

<p align="center">
  <a href="https://evangirardsun.com/">Portfolio ↗</a> &nbsp; / &nbsp;
  <a href="mailto:evangirard50@gmail.com">Email</a> &nbsp; / &nbsp;
  <a href="https://www.linkedin.com/in/evan-girard-sun/">LinkedIn</a>
</p>

I'm an engineering student at Rice University interested in how robots sense the world and move through it. At Phi Lab, I work on camera-based control for small drones. I also build embedded hardware and have designed competition robots.

### Currently working on

<a href="https://github.com/EvanGirardSun/phi-lab-autonomy"><img align="right" src="assets/phi-follow.gif" width="300" alt="An Air75 drone following an AprilTag target in the lab"></a>

**[Camera-based drone autonomy](https://github.com/EvanGirardSun/phi-lab-autonomy)** &nbsp; `2026 · Phi Lab`

A stock Air75 uses its analog video feed to estimate its position relative to AprilTags. A laptop runs the controller and sends commands back through an ExpressLRS radio link.

The repository includes the control loop, camera calibration tools and flight logs. The simulator exercises the same mission logic without connecting to a drone.

[Vision pipeline](https://github.com/EvanGirardSun/phi-lab-autonomy/blob/main/vision.py) · [Controller](https://github.com/EvanGirardSun/phi-lab-autonomy/blob/main/control.py) · [Offline checks](https://github.com/EvanGirardSun/phi-lab-autonomy#try-it-without-a-drone)

<br clear="all">

### On the workbench

| Project | What you'll find | Start here |
| :--- | :--- | :--- |
| **[Phi Lab autonomy](https://github.com/EvanGirardSun/phi-lab-autonomy)** | AprilTag pose estimation, closed-loop control and CRSF communication | [System architecture](https://github.com/EvanGirardSun/phi-lab-autonomy/blob/main/docs/architecture.md) |
| **[Central ECU](https://github.com/EvanGirardSun/central-ecu)** | STM32 carrier-board design with a Python tool that checks the KiCad archive against its BOM and connection list | [Archive checker](https://github.com/EvanGirardSun/central-ecu/blob/main/tools/audit_hardware.py) |
| **[Autonomous mini-vehicle](https://github.com/EvanGirardSun/autonomous-mini-vehicle)** | Original Python from a **2023** WRO team project built around DonkeyCar and EV3 | [Source and project notes](https://github.com/EvanGirardSun/autonomous-mini-vehicle#readme) |

### What I work with

**Python** for vision and control. **OpenCV / NumPy** for pose estimation and calibration. **KiCad** for embedded hardware. I'm interested in the whole path from a noisy sensor reading to something that works on a real machine.

My [portfolio](https://evangirardsun.com/) has the project footage and more of my physical builds, including FireWatch and FRC.

<details>
<summary>About the little robot</summary>

The banner is drawn locally with Python and Pillow. It has light and dark versions, plus a still image for reduced motion.

[Draw the banner](tools/render_banner.py)

```sh
python -m pip install -r requirements.txt
python tools/render_banner.py
```

</details>
