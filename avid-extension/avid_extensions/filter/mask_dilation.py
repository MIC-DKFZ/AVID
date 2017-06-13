# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

import SimpleITK as sitk
from scipy.ndimage.morphology import binary_dilation
import numpy as np
import argparse

def dilate_mask(path_to_mask, output_path, dilation_in_mm=[5,5,5]):
	"""

	:param path_to_mask:
	:param output_path:
	:param dilation_in_mm:
	:returndilateMask.py:
	"""

	mask_img = sitk.ReadImage(path_to_mask)
	mask_arr = sitk.GetArrayFromImage(mask_img).astype(np.uint8)

	direction = mask_img.GetDirection()
	spacing = mask_img.GetSpacing()
	origin = mask_img.GetOrigin()

	# calculate dilation in pixels
	dilation_in_pixels = []
	for i,d in enumerate(dilation_in_mm):
		dilation_in_pixels.append(np.round(d/spacing[i],0).astype(np.uint8))

	# go from XYZ ordering to numpy's ZYX ordering
	dilation = [dilation_in_pixels[2], dilation_in_pixels[1], dilation_in_pixels[0]]

	# perform dilation
	dilated_mask_arr = binary_dilation(mask_arr, structure=np.ones(dilation)).astype(np.uint8)

	# copy geometry data and save dilated mask
	dilated_mask_img = sitk.GetImageFromArray(dilated_mask_arr)
	dilated_mask_img.SetDirection(direction)
	dilated_mask_img.SetSpacing(spacing)
	dilated_mask_img.SetOrigin(origin)

	sitk.WriteImage(dilated_mask_img, output_path)

def dilate_mask_iteratively(path_to_mask, output_path, dilation_in_mm=[5,5,5]):
	"""

	:param path_to_mask:
	:param output_path:
	:param dilation_in_mm:
	:return:
	"""

	mask_img = sitk.ReadImage(path_to_mask)
	mask_arr = sitk.GetArrayFromImage(mask_img).astype(np.uint8)

	direction = mask_img.GetDirection()
	spacing = mask_img.GetSpacing()
	origin = mask_img.GetOrigin()

	# calculate dilation in pixels
	dilation_in_pixels = []
	for i,d in enumerate(dilation_in_mm):
		dilation_in_pixels.append(np.round(d/spacing[i],0).astype(np.uint8))

	# go from XYZ ordering to numpy's ZYX ordering
	dilation = [dilation_in_pixels[2], dilation_in_pixels[1], dilation_in_pixels[0]]

	# prepare iterative dilation
	num_iterations = dilation[0]
	unit_dilation_size = [1, dilation[1]//dilation[0] + 1, dilation[2]//dilation[0] + 1]
	unit_dilation = [2*d + 1 for d in unit_dilation_size]

	# perform dilation
	dilated_mask_arr = binary_dilation(mask_arr, iterations=num_iterations, structure=np.ones(unit_dilation)).astype(np.uint8)

	# copy geometry data and save dilated mask
	dilated_mask_img = sitk.GetImageFromArray(dilated_mask_arr)
	dilated_mask_img.SetDirection(direction)
	dilated_mask_img.SetSpacing(spacing)
	dilated_mask_img.SetOrigin(origin)

	sitk.WriteImage(dilated_mask_img, output_path)

def bounding_box(path_to_mask, output_path, dilation_in_mm=[5,5,5]):
	"""

	:param path_to_mask:
	:param output_path:
	:param dilation_in_mm:
	:return:
	"""

	mask_img = sitk.ReadImage(path_to_mask)
	mask_arr = sitk.GetArrayFromImage(mask_img).astype(np.uint8)

	direction = mask_img.GetDirection()
	spacing = mask_img.GetSpacing()
	origin = mask_img.GetOrigin()

	# calculate dilation in pixels
	dilation_in_pixels = []
	for i,d in enumerate(dilation_in_mm):
		dilation_in_pixels.append(np.round(d/spacing[i],0).astype(np.uint8))

	# go from XYZ ordering to numpy's ZYX ordering
	dilation = [dilation_in_pixels[2], dilation_in_pixels[1], dilation_in_pixels[0]]

	# prepare bounding box
	non_zero_indices = np.nonzero(mask_arr)

	min_z = min(non_zero_indices[0])
	max_z = max(non_zero_indices[0])
	min_y = min(non_zero_indices[1])
	max_y = max(non_zero_indices[1])
	min_x = min(non_zero_indices[2])
	max_x = max(non_zero_indices[2])

	# get bounding box around mask
	mask_arr[min_z-dilation[0]:max_z+dilation[0], min_y-dilation[1]:max_y+dilation[1], min_x-dilation[2]:max_x+dilation[2]] = 1
	dilated_mask_arr = mask_arr

	# copy geometry data and save dilated mask
	dilated_mask_img = sitk.GetImageFromArray(dilated_mask_arr)
	dilated_mask_img.SetDirection(direction)
	dilated_mask_img.SetSpacing(spacing)
	dilated_mask_img.SetOrigin(origin)

	sitk.WriteImage(dilated_mask_img, output_path)


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='binary mask dilation')

	parser.add_argument('-i', '--in_file', type=str, default=None)
	parser.add_argument('-o', '--out_file', type=str, default=None)
	parser.add_argument('-dx', '--dilation_x', type=int, default=5)
	parser.add_argument('-dy', '--dilation_y', type=int, default=5)
	parser.add_argument('-dz', '--dilation_z', type=int, default=5)


	args = parser.parse_args()
	bounding_box(path_to_mask = args.in_file, output_path = args.out_file,
				dilation_in_mm = [args.dilation_x, args.dilation_y, args.dilation_z])



