window.deviceCapabilities = {
    isLowPower: () => {
        const isSlowGPU = /ANGLE \(.*? SwiftShader/.test(renderer);
        return navigator.hardwareConcurrency < 4 || isSlowGPU;
    },
    getRecommendedDensity: () => {
        if (window.deviceCapabilities.isLowPower()) return 'low';
        return window.matchMedia('(min-width: 1200px)').matches ? 'high' : 'medium';
    }
};