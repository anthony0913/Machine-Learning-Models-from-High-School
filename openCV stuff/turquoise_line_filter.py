import cv2
import numpy
import math
from enum import Enum

class GripPipeline:
    def __init__(self):
        """initializes all values to presets or None if need to be set
        """

        self.__hsl_threshold_hue = [43.70503597122302, 107.81569965870308]
        self.__hsl_threshold_saturation = [41.276978417266186, 154.91467576791808]
        self.__hsl_threshold_luminance = [32.10431654676259, 255.0]

        self.hsl_threshold_output = None

        self.__find_lines_input = self.hsl_threshold_output

        self.find_lines_output = None

        self.__filter_lines_lines = self.find_lines_output
        self.__filter_lines_min_length = 10.0
        self.__filter_lines_angle = [0.0, 80.47781569965873]

        self.filter_lines_output = None


    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step HSL_Threshold0:
        self.__hsl_threshold_input = source0
        (self.hsl_threshold_output) = self.__hsl_threshold(self.__hsl_threshold_input, self.__hsl_threshold_hue, self.__hsl_threshold_saturation, self.__hsl_threshold_luminance)

        # Step Find_Lines0:
        self.__find_lines_input = self.hsl_threshold_output
        (self.find_lines_output) = self.__find_lines(self.__find_lines_input)

        # Step Filter_Lines0:
        self.__filter_lines_lines = self.find_lines_output
        (self.filter_lines_output) = self.__filter_lines(self.__filter_lines_lines, self.__filter_lines_min_length, self.__filter_lines_angle)


    @staticmethod
    def __hsl_threshold(input, hue, sat, lum):
        """Segment an image based on hue, saturation, and luminance ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max luminance.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HLS)
        return cv2.inRange(out, (hue[0], lum[0], sat[0]),  (hue[1], lum[1], sat[1]))

    class Line:

        def __init__(self, x1, y1, x2, y2):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2

        def length(self):
            return numpy.sqrt(pow(self.x2 - self.x1, 2) + pow(self.y2 - self.y1, 2))

        def angle(self):
            return math.degrees(math.atan2(self.y2 - self.y1, self.x2 - self.x1))
    @staticmethod
    def __find_lines(input):
        """Finds all line segments in an image.
        Args:
            input: A numpy.ndarray.
        Returns:
            A filtered list of Lines.
        """
        detector = cv2.createLineSegmentDetector()
        if (len(input.shape) == 2 or input.shape[2] == 1):
            lines = detector.detect(input)
        else:
            tmp = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
            lines = detector.detect(tmp)
        output = []
        if len(lines) != 0:
            for i in range(1, len(lines[0])):
                tmp = GripPipeline.Line(lines[0][i, 0][0], lines[0][i, 0][1],
                                lines[0][i, 0][2], lines[0][i, 0][3])
                output.append(tmp)
        return output

    @staticmethod
    def __filter_lines(inputs, min_length, angle):
        """Filters out lines that do not meet certain criteria.
        Args:
            inputs: A list of Lines.
            min_Lenght: The minimum lenght that will be kept.
            angle: The minimum and maximum angles in degrees as a list of two numbers.
        Returns:
            A filtered list of Lines.
        """
        outputs = []
        for line in inputs:
            if (line.length() > min_length):
                if ((line.angle() >= angle[0] and line.angle() <= angle[1]) or
                        (line.angle() + 180.0 >= angle[0] and line.angle() + 180.0 <= angle[1])):
                    outputs.append(line)
        return outputs



