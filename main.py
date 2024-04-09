import cv2
import numpy as np
from os import path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5 import uic
import sys

FORM_CLASS, _ = loadUiType(
    path.join(path.dirname(__file__), "fourier_transform_mixer.ui"))


class ImageProcessor:
    def __init__(self, image_path):
        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        self.fourier_components = {'FT Magnitude': 0,
                                   'FT Phase': 0, 'FT Real': 0, 'FT Imaginary': 0}

    def resize_image(self, target_size):
        self.image = cv2.resize(self.image, target_size)

    def compute_fourier_transform(self):
        # Compute the 2D Fourier Transform
        fourier_transform = np.fft.fft2(self.image)

        # Shift zero frequency components to the center
        fourier_transform_shifted = np.fft.fftshift(fourier_transform)

        # Compute the magnitude and phase
        self.fourier_components['FT Magnitude'] = np.abs(
            fourier_transform_shifted)
        self.fourier_components['FT Phase'] = np.angle(
            fourier_transform_shifted)

        # Compute the real and imaginary parts
        self.fourier_components['FT Real'] = np.real(fourier_transform_shifted)
        self.fourier_components['FT Imaginary'] = np.imag(
            fourier_transform_shifted)

    def get_component(self, component_type):
        # Get the specified Fourier transform component (Magnitude, Phase, Real, Imaginary)
        return self.fourier_components[f'{component_type}']


class ImageViewer:
    def __init__(self, label_widget, component_widget=None, combobox_widget=None):
        self.label_widget = label_widget
        self.component_widget = component_widget
        self.combobox_widget = combobox_widget
        self.image_processor = None
        self.component_pixmap = None
        self.displayed_component = 'FT Magnitude'
        self.brightness_factor = 0.5
        self.contrast_factor = 0.7
        self.dragging = False
        self.last_pos = QPoint()

    def adjust_brightness(self, delta):
        self.brightness_factor += delta/2
        # Ensure it's within bounds
        self.brightness_factor = max(0.1, min(2.0, self.brightness_factor))
        self.apply_brightness_contrast(
            self.brightness_factor, self.contrast_factor)

    def adjust_contrast(self, delta):
        self.contrast_factor += delta/2
        # Ensure it's within bounds
        self.contrast_factor = max(0.1, min(2.0, self.contrast_factor))
        self.apply_brightness_contrast(
            self.brightness_factor, self.contrast_factor)

    def apply_brightness_contrast(self, brightness, contrast):
        if self.image_processor is not None:
            q_image = QImage(self.image_processor.image.data,
                             self.image_processor.image.shape[1], self.image_processor.image.shape[0], QImage.Format_Grayscale8)

            # Create a copy to avoid modifying the original image
            adjusted_image = q_image.copy()
            ptr = adjusted_image.bits()
            ptr.setsize(adjusted_image.byteCount())
            arr = np.frombuffer(ptr, np.uint8).reshape(
                (adjusted_image.height(), adjusted_image.width()))

            # Applying brightness and contrast adjustments directly to pixel values
            arr = np.clip((arr - 128) * contrast + 128 +
                          brightness * 128, 0, 255).astype(np.uint8)

            # Update QImage with the modified pixel values
            q_image = QImage(
                arr, arr.shape[1], arr.shape[0], arr.shape[1], QImage.Format_Grayscale8)

            pixmap = QPixmap.fromImage(q_image)
            self.label_widget.setPixmap(pixmap.scaled(
                self.label_widget.size(), Qt.KeepAspectRatio))

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta_x = (event.pos().x() - self.last_pos.x())/5
            delta_y = (event.pos().y() - self.last_pos.y())/5
            brightness_step = 0.01  # Adjust this step as needed
            # Adjust brightness by dragging left and right
            self.adjust_brightness(delta_x * brightness_step)
            contrast_step = 0.01  # Adjust this step as needed
            # Adjust contrast by dragging up and down
            self.adjust_contrast(delta_y * contrast_step)
            self.last_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def apply_draw_rect_shade(self, value,out):
        if self.image_processor:
            component = self.image_processor.get_component(self.displayed_component)
            component_copy = np.copy(component)
            if value != 0:
                q_image = self.show_fourier_component_image(component_copy)
                self.component_pixmap = QPixmap.fromImage(q_image)
                painter = QPainter()
                painter.begin(q_image)
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                # Calculate rectangle coordinates for the center
                image_width = q_image.width()
                image_height = q_image.height()
            
                rect_width = int(image_width * value/10)
                rect_height = int(image_height * value/10)

                # Make sure rect_x, rect_y, rect_width, rect_height are integers
                rect_x = int((image_width - rect_width)/2)
                rect_y = int((image_height - rect_height)/2)

                # Set the pixels inside the rectangle to True in the mask
                # Draw a rectangle on the image at the center
                pen = QPen(Qt.red)
                painter.setPen(pen)
                painter.drawRect(rect_x, rect_y, rect_width, rect_height)
                if out:
                    # Create a QPainterPath to define the region outside the rectangle
                    path = QPainterPath()
                    path.addRect(0, 0, q_image.width(), q_image.height())

                    # Subtract the rectangle path from the outer region path
                    rect_path = QPainterPath()
                    rect_path.addRect(rect_x, rect_y, rect_width, rect_height)
                    path -= rect_path

                    # Shade the region outside the rectangle
                    shade_color = QColor(0, 0, 0, 100)  # Semi-transparent black
                    painter.fillPath(path, shade_color)
                    for i in range(rect_x, rect_x + rect_width):
                        for j in range(rect_y, rect_y + rect_height):
                            component_copy[j][i] = 0
                else :
                    shade_color = QColor(0, 0, 0, 100)  # Semi-transparent black
                    painter.fillRect(rect_x, rect_y, rect_width, rect_height, shade_color)
                    
                    # Zero values outside the rectangle in the component array
        
                    for i in range(image_width):
                        for j in range(image_height):
                            if i < rect_x or i >= rect_x + rect_width \
                                or j < rect_y or j >= rect_y + rect_height:
                                component_copy[j][i] = 0
                painter.end()
                self.component_pixmap = QPixmap.fromImage(q_image)
                self.component_widget.setPixmap(self.component_pixmap.scaled(
                            self.component_widget.size(), Qt.KeepAspectRatio))
                
                return component_copy
            else :
                self.show_fourier_component_image(component_copy)
                return component_copy

    def show_image(self):
        if self.image_processor is not None:
            # Set an empty pixmap to clear the image
            self.label_widget.setPixmap(QPixmap())
            q_image = QImage(self.image_processor.image.data,
                             self.image_processor.image.shape[1], self.image_processor.image.shape[0], QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.label_widget.setPixmap(pixmap.scaled(
                self.label_widget.size(), Qt.KeepAspectRatio))

    def create_q_image(self, component):
        bytes_per_line = component.shape[1]
        q_image = QImage(component.data.tobytes(), component.shape[1], component.shape[0],
                         bytes_per_line, QImage.Format_Grayscale8)

        return q_image

    def show_fourier_component_image(self, component):
        if self.displayed_component == 'FT Magnitude':
            component = np.log(1+component)
            component = (component / np.max(component) * 255).astype(np.uint8)
        else:
            component = (component - np.min(component)) / \
                (np.max(component) - np.min(component)) * 255

        q_image = self.create_q_image(component)
        self.component_pixmap = QPixmap.fromImage(q_image)

        self.component_widget.setPixmap(self.component_pixmap.scaled(
            self.component_widget.size(), Qt.KeepAspectRatio))

        return q_image

    def change_displayed_component(self, new_component):
        self.displayed_component = new_component
        new_component_arr = self.image_processor.get_component(new_component)
        self.show_fourier_component_image(new_component_arr)

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.label_widget,
            "Open Image",
            "",
            "Image Files (*.png *.jpg *.bmp);;All Files (*)",
        )
        if file_path:
            self.image_processor = ImageProcessor(file_path)

class Mixer:
    def __init__(self):
        self.weights = [0.0, 0.0, 0.0, 0.0]
        self.selected_components = [
            [], [], [], []]

    def set_weights(self, index, value):
        # Set weight for a specific index
        self.weights[index] = value / 10.0

    def set_component(self, index, component):
        # Set component for a specific index
        self.selected_components[index] = component

    def mix_and_reconstruct(self, comp1, comp2, category):
        # Reconstruct the mixed image
        if category == 'Magnitude & Phase':
            mixed_complex = comp1 * np.exp(1j * comp2)
        else:
            mixed_complex = comp1 + 1j * comp2

        mixed_complex = np.fft.ifftshift(mixed_complex)
        mixed_image = np.fft.ifft2(mixed_complex)
        mixed_image = np.abs(mixed_image)  # Ensure non-negative values
        mixed_image -= mixed_image.min()  # Normalize
        mixed_image = (mixed_image / mixed_image.max()) * 255  # Scale to 0-255
        mixed_image = mixed_image.astype(np.uint8)
        return mixed_image

    def mix_images(self, category, selected_components_names):
        if category == 'Magnitude & Phase':
            comp1, comp2 = self.create_mixed_components(
                'FT Magnitude', 'FT Phase', selected_components_names)
        else:
            comp1, comp2 = self.create_mixed_components(
                'FT Real', 'FT Imaginary', selected_components_names)
        mixed_image = self.mix_and_reconstruct(comp1, comp2, category)
        return mixed_image

    def create_mixed_components(self, s1, s2, selected_components_names):
        comp1 = [0.0]*len(self.selected_components[0])
        comp2 = [0.0]*len(self.selected_components[0])
        for index, selected_component in enumerate(selected_components_names):
            if selected_component == s1:
                comp1 += self.weights[index]*self.selected_components[index]
            else:
                comp2 += self.weights[index]*self.selected_components[index]
        return comp1, comp2

class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        self.setupUi(self)
        self.progressBar.hide()

        self.image_viewers = [
            ImageViewer(self.image1, self.image1_components,
                        self.image1_combobox),
            ImageViewer(self.image2, self.image2_components,
                        self.image2_combobox),
            ImageViewer(self.image3, self.image3_components,
                        self.image3_combobox),
            ImageViewer(self.image4, self.image4_components,
                        self.image4_combobox)
        ]

        for index, image_viewer in enumerate(self.image_viewers):
            image_viewer_label = getattr(self, f"image{index + 1}")
            image_viewer_label.mousePressEvent = lambda event, viewer=image_viewer: viewer.mousePressEvent(
                event)
            image_viewer_label.mouseMoveEvent = lambda event, viewer=image_viewer: viewer.mouseMoveEvent(
                event)
            image_viewer_label.mouseReleaseEvent = lambda event, viewer=image_viewer: viewer.mouseReleaseEvent(
                event)
            image_viewer_label.mouseDoubleClickEvent = lambda event, viewer=image_viewer: self.mouseDoubleClickEvent(
                event,viewer,index)
            
            
        self.image1_combobox.currentTextChanged.connect(
            lambda text: self.change_displayed_component(0, text, self.image_viewers[0]))
        self.image2_combobox.currentTextChanged.connect(
            lambda text: self.change_displayed_component(1, text, self.image_viewers[1]))
        self.image3_combobox.currentTextChanged.connect(
            lambda text: self.change_displayed_component(2, text, self.image_viewers[2]))
        self.image4_combobox.currentTextChanged.connect(
            lambda text: self.change_displayed_component(3, text, self.image_viewers[3]))

        self.mixer = Mixer()

        # Connect slider value changes to Mixer methods
        self.component1_slider.valueChanged.connect(
            lambda value: self.mixer.set_weights(0, value))
        self.component2_slider.valueChanged.connect(
            lambda value: self.mixer.set_weights(1, value))
        self.component3_slider.valueChanged.connect(
            lambda value: self.mixer.set_weights(2, value))
        self.component4_slider.valueChanged.connect(
            lambda value: self.mixer.set_weights(3, value))

        self.square_size_slider.setMinimum(1)
        self.square_size_slider.setMaximum(10)
        self.square_size_slider.setValue(1)
        self.square_size_slider.setTickInterval(1)
        self.radio_btn_nothing.toggled.connect(self.update_square)
        self.radio_btn_draw_rect_shade_outside.toggled.connect(
            self.update_square)
        self.radio_btn_draw_rect_shade_inside.toggled.connect(
            self.update_square)
        self.square_size_slider.valueChanged.connect(self.update_square)
        # self.apply_button.clicked.connect(self.mix_images)
        self.component1_slider.valueChanged.connect(self.mix_images)
        self.component2_slider.valueChanged.connect(self.mix_images)
        self.component3_slider.valueChanged.connect(self.mix_images)
        self.component4_slider.valueChanged.connect(self.mix_images)
        self.square_size_slider.valueChanged.connect(self.mix_images)

    def mouseDoubleClickEvent(self,event,viewer,index):
        if event.button() == Qt.RightButton:
            viewer.show_image()
        else:
            self.add_image(index,viewer)
            
    def update_square(self):
        value = self.square_size_slider.value()
        for index, viewer in enumerate(self.image_viewers):
            if viewer.image_processor is not None and viewer.displayed_component:
                if self.radio_btn_draw_rect_shade_outside.isChecked():
                    new_component_arr = viewer.apply_draw_rect_shade(
                        value, True)
                    self.mixer.set_component(index, new_component_arr)

                elif self.radio_btn_draw_rect_shade_inside.isChecked():
                    new_component_arr = viewer.apply_draw_rect_shade(
                        value, False)
                    self.mixer.set_component(index, new_component_arr)

                elif self.radio_btn_nothing.isChecked():
                    new_component_arr = viewer.apply_draw_rect_shade(0, True)
                    self.mixer.set_component(index, new_component_arr)

    def add_image(self, index, image_viewer):
        image_viewer.browse_image()
        if image_viewer.image_processor is not None:
            self.resize_images()
            for viewer in self.image_viewers:
                viewer.show_image()
            image_viewer.image_processor.compute_fourier_transform()
            self.change_displayed_component(
                index, 'FT Magnitude', image_viewer)
            self.mixer.set_component(
                index, image_viewer.image_processor.get_component('FT Magnitude'))

    def change_displayed_component(self, index,  component, image_viewer):
        if image_viewer.image_processor:
            image_viewer.change_displayed_component(component)
        self.mixer.set_component(
            index, image_viewer.image_processor.get_component(component))
        self.update_square()
        
    def resize_images(self):
        min_size = self.get_min_size()
        for image_viewer in self.image_viewers:
            if image_viewer.image_processor:
                image_viewer.image_processor.resize_image(min_size)

    def get_min_size(self):
        min_size = self.image_viewers[0].image_processor.image.shape
        for image_viewer in self.image_viewers:
            if image_viewer.image_processor:
                if image_viewer.image_processor.image.shape[0] < min_size[0] and image_viewer.image_processor.image.shape[1] < min_size[1]:
                    min_size = image_viewer.image_processor.image.shape
        return min_size

    def mix_images(self):
        selected_components = [
            viewer.combobox_widget.currentText() for viewer in self.image_viewers]
        if all(item == selected_components[0] for item in selected_components):
            QMessageBox.warning(
                self, 'Warning', 'The selected components should not be all the same.')
        elif self.comboBox_category.currentText()== "Magnitude & Phase" and "FT Real" in selected_components:
            QMessageBox.warning(
                self, 'Warning', 'The selected components should all be the same category.')
        elif self.comboBox_category.currentText()== "Magnitude & Phase" and "FT Imaginary" in selected_components:
            QMessageBox.warning(
                self, 'Warning', 'The selected components should all be the same category.')
        elif self.comboBox_category.currentText()== "Real & Imaginary" and "FT Magnitude" in selected_components:
            QMessageBox.warning(
                self, 'Warning', 'The selected components should all be the same category.')
        elif self.comboBox_category.currentText()== "Real & Imaginary" and "FT Phase" in selected_components:
            QMessageBox.warning(
                self, 'Warning', 'The selected components should all be the same category.')
        else:
            mixed_image = self.mixer.mix_images(
                self.comboBox_category.currentText(), selected_components)

            self.display_mixed_image(mixed_image)

    def display_mixed_image(self, mixed_image):
        if self.channel1_radiobutton.isChecked():
            label_widget=self.output_viewer1
        else:
            label_widget=self.output_viewer2
        label_widget.setPixmap(QPixmap())
        height, width = len(mixed_image), len(mixed_image[0])

        # Create a QPixmap and a QPainter to draw on it
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(255, 255, 255))  # Fill with a white background

        painter = QPainter(pixmap)

        for y in range(height):
            for x in range(width):
                pixel_value = mixed_image[y][x]
                color = QColor(pixel_value, pixel_value, pixel_value)
                painter.setPen(color)
                painter.drawPoint(x, y)

        painter.end()
        label_widget.setPixmap(pixmap.scaled(
            label_widget.size(), Qt.KeepAspectRatio))

    def exit_program(self):
        sys.exit()


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
