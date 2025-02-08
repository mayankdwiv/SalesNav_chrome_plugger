function updateSelectedOptions(selectElement, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    Array.from(selectElement.selectedOptions).forEach(option => {
      const tag = document.createElement('div');
      tag.className = 'tag';
      tag.innerHTML = `
        ${option.text}
        <span class="tag-remove" onclick="removeOption('${selectElement.name}', '${option.value}', '${containerId}')">×</span>
      `;
      container.appendChild(tag);
    });
  }

  function removeOption(selectName, value, containerId) {
    const selectElement = document.querySelector(`select[name="${selectName}"]`);
    const option = selectElement.querySelector(`option[value="${value}"]`);
    option.selected = false;
    updateSelectedOptions(selectElement, containerId);
  }

  document.querySelectorAll('.multi-select select').forEach(select => {
    select.addEventListener('change', () => {
      const containerId = select.name === 'Company_headcount' ? 'company-size-selected' : 'geography-selected';
      updateSelectedOptions(select, containerId);
    });
  });