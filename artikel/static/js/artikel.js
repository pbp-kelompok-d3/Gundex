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

    setInterval(slideNext, 4000); // Geser setiap 4 detik
});