# BodyMap

The `BodyMap` class provides a functionality to generate a body map visualization based on specific areas of the human body and corresponding values. It uses the `matplotlib` library to create the visualization.

## Installation

To use the `BodyMap` class, you need to have `matplotlib` installed in your Python environment. You can install it using pip:

```
pip install matplotlib
```

## Usage

1. Import the necessary libraries:

```python
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import cm
```

2. Define an instance of the `BodyMap` class:

```python
body_map = BodyMap()
```

3. Generate the body map visualization by specifying the areas and corresponding values:

```python
areas = ['head', 'legs', 'right leg', 'left leg', 'right arm', 'left arm', 'torso', 'arms', 'waist', 'neck',
         'left hand', 'right hand', 'upper right arm', 'upper left arm', 'right forearm', 'left forearm',
         'right thigh', 'left thigh', 'right lower leg', 'left lower leg']
values = [0.5, 0.8, 0.2, 0.6, 0.9, 0.4, 0.7, 0.3, 0.1, 0.5, 0.6, 0.4, 0.7, 0.3, 0.8, 0.2, 0.9, 0.3, 0.7, 0.5]

body_map.generate(areas, values)
```

4. Customize the visualization (optional):

```python
# Specify the size of the figure (default: (9, 15))
figsize = (10, 8)

# Specify the colormap to use (default: 'coolwarm')
cmap = 'viridis'

# Specify the background color ('white' or 'black', default: 'white')
background = 'white'

body_map.generate(areas, values, figsize=figsize, cmap=cmap, background=background)
```

5. Display the visualization:

```python
plt.show()
```

## Example
```python
ax = BodyMap().generate(areas=['head','torso','left hand','right foot'],values=[10,30,22,12],cmap='coolwarm',background='white')
plt.show()
```
