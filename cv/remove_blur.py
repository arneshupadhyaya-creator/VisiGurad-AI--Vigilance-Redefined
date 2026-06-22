import cv2 as cv
import numpy as np

def wiener_filter(img, psf, K=0.01):
    """
    Applies a Wiener filter to an image.
    img: Grayscale degraded image
    psf: Point Spread Function (the blur kernel)
    K: Constant representing Noise-to-Signal ratio (Sn/Sf)
    """
    # Convert to float32
    img = img.astype(np.float32)
    
    # 1. Take the 2D Fast Fourier Transform of the image and the PSF
    img_fft = np.fft.fft2(img)
    psf_fft = np.fft.fft2(psf, s=img.shape) # Match size to image
    
    # 2. Calculate the complex conjugate of the PSF
    psf_fft_conj = np.conj(psf_fft)
    
    # 3. Apply the Wiener Filter formula
    # W = H* / (|H|^2 + K)
    psf_fft_mag_sq = np.abs(psf_fft) ** 2
    wiener_kernel = psf_fft_conj / (psf_fft_mag_sq + K)
    
    # 4. Multiply the degraded image's FFT by our Wiener kernel
    result_fft = img_fft * wiener_kernel
    
    # 5. Take the Inverse FFT to convert back to the spatial image domain
    result = np.fft.ifft2(result_fft)
    result = np.abs(result) # Take real magnitude
    
    # Clip values to valid [0, 255] range
    return np.clip(result, 0, 255).astype(np.uint8)


blurry_img = cv.imread('E:/CV/data/text.jpg', cv.IMREAD_GRAYSCALE)

# Create a simulated Blur Kernel (PSF) - e.g., a 5x5 Gaussian blur kernel
psf = cv.getGaussianKernel(5, 1.5)
psf = np.outer(psf, psf)

# Apply the filter (Adjust 'K' if the image is too noisy or still blurry)
deblurred_img = wiener_filter(blurry_img, psf, K=0.015)

cv.imwrite('deblurred_wiener.jpg', deblurred_img)
