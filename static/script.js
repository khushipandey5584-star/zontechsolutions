
const menuToggle = document.getElementById("menuToggle");
const navLinks = document.getElementById("navLinks");
const contactForm = document.getElementById("contactForm");
const formStatus = document.getElementById("formStatus");
const submitBtn = document.getElementById("submitBtn");

// Mobile navigation
menuToggle.addEventListener("click", () => {
    navLinks.classList.toggle("open");
    menuToggle.setAttribute(
        "aria-expanded",
        navLinks.classList.contains("open")
    );
});

navLinks.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
        navLinks.classList.remove("open");
        menuToggle.setAttribute("aria-expanded", "false");
    });
});

// Current year
document.getElementById("year").textContent = new Date().getFullYear();

// Scroll reveal animation
const revealElements = document.querySelectorAll(
    ".service-card, .project-card, .process-step, .section-content"
);

revealElements.forEach((element) => {
    element.classList.add("reveal");
});

if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    revealElements.forEach((element) => observer.observe(element));
} else {
    revealElements.forEach((element) => element.classList.add("visible"));
}

// Contact form: send inquiry to Flask backend
contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    formStatus.textContent = "";
    formStatus.className = "form-status";
    submitBtn.disabled = true;
    submitBtn.textContent = "Sending...";

    const inquiry = {
        name: document.getElementById("name").value.trim(),
        email: document.getElementById("email").value.trim(),
        service: document.getElementById("service").value,
        message: document.getElementById("message").value.trim(),
        website: document.getElementById("website").value.trim()
    };

    try {
        const response = await fetch("/api/contact", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(inquiry)
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Unable to submit your inquiry.");
        }

        formStatus.textContent = result.message;
        formStatus.classList.add("success");
        contactForm.reset();

    } catch (error) {
        formStatus.textContent =
            error.message || "Something went wrong. Please try again.";
        formStatus.classList.add("error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Send Inquiry ↗";
    }
});
