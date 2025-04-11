const nous = (str) => {
  /* Replaces underscore with dash */
  return str.replace(/_/g, '-');
}

const nosp = (str) => {
  /* Replaces spaces with _ */
  return str.replace(/ /g, '_');
}

const empty = (obj) => {
  return Object.keys(obj).length === 0 && obj.constructor === Object;
}

const removeClassesByPrefix = (element, prefix) => {
  for (let i = element.classList.length - 1; i >= 0; i--) {
    const className = element.classList[i];
    if (className.startsWith(prefix)) {
      element.classList.remove(className);
    }
  }
  return;
}

const isBoolean = (value) => "boolean" === typeof value;
const formatBoolean = (value) => value ? "Yes" : "No"

const formatMotion = (element, value) => {
  // If the motion is true, select everything with that motion and blink
  value ? element.classList.add("blinking") : element.classList.remove("blinking");
  return;
}

const formatSiteState = (element, value) => {
  /* Formats the site states for display */
  removeClassesByPrefix(element, "text-");
  if (value === "Closed") {
    element.classList.add("text-warning");
  }
  else if (value === "Opened") {
    element.classList.add("text-success");
  }
  else if (value === "Ajar") {
    element.classList.add("text-info");
  }
  else {
    element.textContent = "Error";
    element.classList.add("text-danger");
    return;
  }
  element.textContent = value;
  return;
}

const formatLimit = (element, value) => {
  removeClassesByPrefix(element, "bg-");
  if (value === "h2") {
    element.classList.add("bg-danger", "blinking");
    element.textContent = value.toUpperCase();
  }
  else if (value === "s2") {
    element.classList.add("bg-danger", "blinking");
    element.textContent = value.toUpperCase();
  }
  else if (value === "h1") {
    element.classList.add("bg-warning");
    element.classList.remove("blinking");
    element.textContent = value.toUpperCase();
  }
  else if (value === "s1") {
    element.classList.add("bg-warning");
    element.classList.remove("blinking");
    element.textContent = value.toUpperCase();
  }
  else {
    element.classList.add("bg-transparent");
    element.textContent = value;
    element.classList.remove("blinking");
  }
}
