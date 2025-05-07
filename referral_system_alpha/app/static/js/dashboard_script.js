document.addEventListener("DOMContentLoaded", () => {
    const thumbnail = document.getElementsByClassName("thumbnail-img")[0];
    const uploadBox = document.getElementById("uploadBox");
    const uploadButton = document.getElementById("uploadButton");
    const fileButton = document.getElementById("fileInput");
    const myLabel = document.querySelector('label');
    const para = document.getElementById("upload-text")
    const copyIcon = document.querySelector('.fa-copy');
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
    myLabel.addEventListener('click', (e) => {
      e.stopPropagation(); // Prevents the label from triggering input
    });
    if (fileButton.files.length === 0){
      uploadButton.disabled = true;
    }
    fileButton.addEventListener("click",(event) => {
      event.stopPropagation()
      if(fileButton.files.length > 0){
        uploadButton.disabled = false;
        para.innerText = fileButton.files[0].filename;
      }

    })
    fileButton.addEventListener("change",(event) => {
      event.stopPropagation()
      if(fileButton.files.length > 0){
        uploadButton.disabled = false;
        console.log(fileButton.files[0])
        para.innerText = fileButton.files[0].name
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
    copyIcon.addEventListener("click", () => {
      const copyText = document.getElementById("ref_code_a");
      
      navigator.clipboard.writeText(copyText.href)
        .then(() => {
          // Remove any existing toast first
          const existingToast = document.querySelector('.copy-toast');
          if (existingToast) existingToast.remove();
    
          // Create toast element
          const toast = document.createElement('div');
          toast.className = 'copy-toast';
          toast.textContent = 'Copied!';
          
          // Position it near the icon
          positionToast(copyIcon, toast);
          
          // Add to DOM
          document.body.appendChild(toast);
          
          // Auto-remove after delay
          setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 300);
          }, 800);
        })
        .catch(err => {
          console.error('Failed to copy:', err);
        });
    });
    
    function positionToast(iconElement, toastElement) {
      const iconRect = iconElement.getBoundingClientRect();
      const toastWidth = 100; // Approximate width
      const toastHeight = 40; // Approximate height
      
      // Calculate position (centered below icon)
      let left = iconRect.left + window.scrollX + (iconRect.width / 2) - (toastWidth / 2);
      let top = iconRect.bottom + window.scrollY + 5;
      
      // Keep within viewport bounds
      left = Math.max(10, Math.min(left, window.innerWidth - toastWidth - 10));
      
      toastElement.style.left = `${left}px`;
      toastElement.style.top = `${top}px`;
    }
  });