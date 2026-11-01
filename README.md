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

**[Camera-based drone autonomy](https://github.com/EvanGirardSun/phi-lab-autonomy)** &nbsp; `2026 · Phi Lab`

A stock Air75 uses its analog video feed to estimate its position relative to AprilTags. A laptop runs the controller and sends commands back through an ExpressLRS radio link.

The repository includes the control loop, camera calibration tools and flight logs. The simulator exercises the same mission logic without connecting to a drone.

[Vision pipeline](https://github.com/EvanGirardSun/phi-lab-autonomy/blob/main/vision.py) · [Controller](https://github.com/EvanGirardSun/phi-lab-autonomy/blob/main/control.py) · [Watch a flight ↗](https://evangirardsun.com/assets/phi-follow-v5.mp4)

<a href="https://github.com/EvanGirardSun/phi-lab-autonomy/blob/main/docs/architecture.md">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="assets/control-loop-light.png">
    <img src="assets/control-loop-dark.png" width="100%" alt="Drone control pipeline: camera capture, AprilTag pose, mission controller, CRSF radio link. Open the system architecture.">
  </picture>
</a>

[![Phi Lab offline checks](https://github.com/EvanGirardSun/phi-lab-autonomy/actions/workflows/offline.yml/badge.svg)](https://github.com/EvanGirardSun/phi-lab-autonomy/actions/workflows/offline.yml)

### Other code

| Project | What you'll find | Start here |
| :--- | :--- | :--- |
| **[Central ECU](https://github.com/EvanGirardSun/central-ecu)** | STM32 carrier-board design with a Python tool that checks the KiCad archive against its BOM and connection list | [Archive checker](https://github.com/EvanGirardSun/central-ecu/blob/main/tools/audit_hardware.py) |
| **[Autonomous mini-vehicle](https://github.com/EvanGirardSun/autonomous-mini-vehicle)** | Original Python from a **2023** WRO team project built around DonkeyCar and EV3 | [Source and project notes](https://github.com/EvanGirardSun/autonomous-mini-vehicle#readme) |

### What I work with

**Python** for vision and control. **OpenCV / NumPy** for pose estimation and calibration. **KiCad** for embedded hardware. I'm interested in the whole path from a noisy sensor reading to something that works on a real machine.

My [portfolio](https://evangirardsun.com/) has the project footage and more of my physical builds, including FireWatch and FRC.

<details>
<summary>About the little robot</summary>

The mascot and control-loop strip are drawn locally with Python and Pillow. They have light and dark versions, and the animated banner has a still image for reduced motion.

[Draw the banner](tools/render_banner.py)

```sh
python -m pip install -r requirements.txt
python tools/render_banner.py
```

</details>
