document.addEventListener("DOMContentLoaded", () => {
    const thumbnail = document.getElementsByClassName("thumbnail-img")[0];
    const uploadBox = document.getElementById("uploadBox");
    const uploadButton = document.getElementById("uploadButton");
    const fileButton = document.getElementById("fileInput")
    uploadBox.ondragover = function(evt){
      evt.preventDefault();
      evt.stopPropagation();
      uploadBox.classList.add('active');
    } 
    uploadBox.ondragleave = function(evt){
      evt.preventDefault();
      evt.stopPropagation();
      uploadBox.classList.remove('active');
    } 
    uploadBox.ondragenter = function(evt){
      evt.preventDefault();
      evt.stopPropagation();
      uploadBox.classList.add('active');
    }  
    uploadBox.ondrop = function(evt){
      evt.preventDefault()
      fileButton.files = evt.dataTransfer.files
      uploadBox.classList.remove('active');
      uploadButton.disabled = false;
    }
    if (fileButton.files.length === 0){
      uploadButton.disabled = true;
    }
    fileButton.addEventListener("click",(event) => {
      event.stopPropagation()
      if(fileButton.files.length > 0){
        uploadButton.disabled = false;
      }
      console.log(fileButton.files.length)

    })
    fileButton.addEventListener("change",(event) => {
      event.stopPropagation()
      if(fileButton.files.length > 0){
        uploadButton.disabled = false;
      }

    })
    // console.log(thumbnail)
    // Add a click event listener to the thumbnail
   
    thumbnail.addEventListener("click", () => {
      uploadBox.classList.toggle("visible");
    });
    uploadBox.addEventListener("click",()=>{
      uploadBox.classList.toggle("visible");
    })
  });