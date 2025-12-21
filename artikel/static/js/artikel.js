document.addEventListener("DOMContentLoaded", function() {
    const carouselInner = document.getElementById("carousel-inner");
    if (!carouselInner) return;

    let index = 0;
    const totalSlides = carouselInner.children.length;

    function slideNext() {
        if (totalSlides === 0) return;
        index = (index + 1) % totalSlides;
        carouselInner.style.transform = `translateX(-${index * 100}%)`;
    }

<<<<<<< HEAD
    setInterval(slideNext, 4000); // Geser setiap 4 detik
=======
    setInterval(slideNext, 8000); // Geser setiap 8 detik
>>>>>>> 0d85c9f1061ae6957fadf6d4d17f1148a26b6ac9
});