import SimpleITK as sitk
from scipy.ndimage.morphology import binary_dilation
import numpy as np
import argparse

def dilate_mask(path_to_mask, output_path, dilation_in_mm=[5,5,5]):
	"""
    Loads a given mask image dilates it and stores it in the given output path.
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

	# perform dilation
	dilated_mask_arr = binary_dilation(mask_arr, structure=np.ones(dilation)).astype(np.uint8)

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
	dilate_mask(path_to_mask = args.in_file, output_path = args.out_file,
				dilation_in_mm = [args.dilation_x, args.dilation_y, args.dilation_z])



