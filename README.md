# Master's Thesis: Automata Learning of Websites Using AALpy and Selenium

This repository contains the code of the learning application described in the master's thesis "Automata Learning of Websites Using AALpy and Selenium", submitted by Lena Klambauer at Graz University of Technology in September 2025.

The learning application can be executed with the provided example configuration file as follows:

```
python start_with_example_config.py
```

To use a different configuration, different values must be set in the configuration file as described in the thesis (see Chapter 4 - Implementation > Configuration File).

All code related to the learning application itself can be found in the `website_learning` directory. Any results created will be placed in the `Results` and `StoredResults` subdirectories.

## Dependencies and Reproducibility

This project was developed and tested with the Python package versions and system-level dependencies listed below. 
While the project may work with other versions of the dependencies, reproducibility is only guaranteed with the specified versions.

| Type              | Dependency    | Version        |
|-------------------|---------------|----------------|
| Python package    | aalpy         | 1.5.1          |
| Python package    | PyYAML        | 6.0.2          |
| Python package    | selenium      | 4.17.2         |
| System dependency | Google Chrome | 140.0.7339.128 |
| System dependency | ChromeDriver  | 140.0.7339.82  |