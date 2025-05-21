async function uploadImages() {
    let files = document.getElementById('imageUploader').files;
    if (files.length === 0) {
        alert("Seleziona almeno un'immagine");
        return;
    }

    let linksDiv = document.getElementById("imageLinks");
    let previewDiv = document.getElementById("imagePreview");
    let editor = CKEDITOR.instances.body;
    let imageUrls = [];

    linksDiv.innerHTML = "<p>Caricamento in corso... ⏳</p>";
    previewDiv.innerHTML = "";

    let uploadPromises = Array.from(files).map(async (file) => {
        let formData = new FormData();
        formData.append("file", file);
        formData.append("upload_preset", "blog_images"); // Preset di Cloudinary

        // Mostra l'anteprima dell'immagine
        let reader = new FileReader();
        reader.onload = function (e) {
            let imgPreview = document.createElement("img");
            imgPreview.src = e.target.result;
            imgPreview.style.maxWidth = "100px";
            imgPreview.style.margin = "5px";
            previewDiv.appendChild(imgPreview);
        };
        reader.readAsDataURL(file);

        try {
            let response = await fetch("https://api.cloudinary.com/v1_1/dhl1h30hp/image/upload", {
                method: "POST",
                body: formData
            });

            let data = await response.json();
            let link = data.secure_url;
            imageUrls.push(link);

            let altText = prompt(`Inserisci la descrizione per "${file.name}" (Alt text):`, "Immagine");
            let imageHtml = `<img src="${link}" alt="${altText}" style="max-width:100%;">`;

            // Inserisce l'immagine nel corpo dell'editor
            editor.insertHtml(imageHtml);

            // Mostra il link dell'immagine caricata
            let imageLink = document.createElement("p");
            imageLink.innerHTML = `✅ <a href="${link}" target="_blank">${link}</a> (Alt: ${altText})`;
            linksDiv.appendChild(imageLink);
        } catch (error) {
            console.error("Errore nel caricamento dell'immagine:", error);
            let errorText = document.createElement("p");
            errorText.textContent = `❌ Errore nel caricamento di ${file.name}`;
            errorText.style.color = "red";
            linksDiv.appendChild(errorText);
        }
    });

    await Promise.all(uploadPromises);
    document.getElementById('img_urls').value = JSON.stringify(imageUrls);
    linksDiv.innerHTML += "<p>✔️ Tutte le immagini sono state caricate!</p>";
}
