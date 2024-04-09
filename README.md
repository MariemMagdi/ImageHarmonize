# ImageHarmonize

This desktop program demonstrates the significance of magnitude and phase components in a signal by visualizing their effects on images using Fourier Transform (FT). Though implemented on 2D grayscale images for clarity, the concepts apply universally to signals. 

## Features

### Image Viewers

- **Open and View Images:** The program allows opening and viewing up to four grayscale images simultaneously.
  - **Conversion:** Colored images are automatically converted to grayscale upon opening.
  - **Unified Size:** Images are resized to match the smallest image's dimensions.
  - **FT Components:** Each image has two displays:
    - A fixed display for the image itself.
    - A dynamic display showing selected FT components: Magnitude, Phase, Real, or Imaginary.
  - **Easy Browse:** Images can be changed by double-clicking on the respective viewer.

### Output Ports

- **Mixer Result:** The result of mixing images can be viewed in one of two output viewports, mirroring the input image viewports.
- **Control:** Users choose where the mixer result appears.

### Brightness/Contrast Adjustment

- **User Control:** Adjust the brightness and contrast of images and FT components via mouse dragging.
- **Universal Adjustment:** Brightness/contrast adjustments are applicable to all four components.

### Components Mixer

- **Customized Weighting:** Output image is the inverse Fourier Transform (ifft) of a weighted average of the FT of the input images.
- **User Interface:** Intuitive sliders allow users to customize weights for each image's FT components.

### Regions Mixer

- **Region Selection:** Users can choose regions for each FT component: inner (low frequencies) or outer (high frequencies).
- **Visual Feedback:** Selected regions are highlighted via semi-transparent coloring or hashing.
- **Customizable Size:** Users can adjust the size or percentage of the selected region using sliders or resize handles.

### Realtime Mixing

- **Progress Feedback:** During lengthy ifft operations, a progress bar indicates the process's status.
- **Concurrency Handling:** If the user initiates a new mixing operation while a previous one is ongoing, the program cancels the prior operation and starts the new request.


## Snapshots (mixing is between the first two images for simplicity)

1. Initial view of the program ![Screenshot 2024-04-09 223957](https://github.com/MariemMagdi/ImageHarmonize/assets/104202307/c77352a9-a528-47db-a167-2953176d790d)
2. Brightness/contrast adjustment ![Screenshot 2024-04-09 224409](https://github.com/MariemMagdi/ImageHarmonize/assets/104202307/ec5dea3c-e123-4d85-8cd6-8dae959d8e56)

3. Weight customization sliders with full window mode and real/imaginary components![Screenshot 2024-04-09 225443](https://github.com/MariemMagdi/ImageHarmonize/assets/104202307/f6e99d4a-ffca-4d71-9f03-34cec0eafcb2)

4. Weight customization sliders with inner window mode and magnitude/phase components![Screenshot 2024-04-09 225756](https://github.com/MariemMagdi/ImageHarmonize/assets/104202307/e6ab6973-4fd8-46a5-b1af-3bc9e15f4596)

5. Weight customization sliders with outer window mode and magnitude/phase components![Screenshot 2024-04-09 225836](https://github.com/MariemMagdi/ImageHarmonize/assets/104202307/cdd5cec7-c24e-4434-8a2e-4395512a7c73)



## Contributing

1. Ali Maged
2. Mina Adel
3. Mariem Magdy
4. Mariam Hany
   
Under the supervision of Dr.Tamer Basha, SBME 2025
