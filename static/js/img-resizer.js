document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".blog-content img").forEach(img => {
        img.style.maxWidth = "100%";
        img.style.height = "auto";
        img.style.display = "block";
        img.style.margin = "20px auto";
        img.style.maxHeight = "500px";
        img.style.objectFit = "cover";
    });
});
