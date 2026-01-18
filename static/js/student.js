// Student Form JavaScript
document.addEventListener('DOMContentLoaded', () => {
    // Course data
    const courses = {
        UG: ["BA(PSY)", "BA(MMC)", "B.COM", "BMS", "BAF", "B.Sc-IT", "BCA"],
        PG: ["M.Com(Accountancy)", "M.Com(Business Management)", "M.Sc-IT"],
        JC: ["Science", "Arts", "Commerce"]
    };

    const years = {
        UG: ["First Year", "Second Year", "Third Year"],
        PG: ["First Year", "Second Year"]
    };

    // Get DOM elements
    const levelSelect = document.getElementById("level");
    const courseSelect = document.getElementById("course");
    const yearSelect = document.getElementById("year");
    const jcFields = document.getElementById("jcFields");
    const jcYearSelect = document.getElementById("jcYear");
    const jcStreamSelect = document.getElementById("jcStream");
    const visitorForm = document.getElementById("visitorForm");

    // Update date and time
    function updateDateTime() {
        const now = new Date();
        const formattedDate = now.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        const formattedDay = now.toLocaleDateString("en-US", { 
            weekday: "long" 
        });
        
        document.getElementById("currentDate").textContent = formattedDate;
        document.getElementById("currentDay").textContent = formattedDay;
        
        setTimeout(updateDateTime, 60000);
    }

    updateDateTime();

    // Level change handler
    levelSelect.addEventListener("change", function() {
        const level = this.value;
        
        // Reset dependent fields
        courseSelect.innerHTML = '<option value="">Select Course / Stream</option>';
        yearSelect.innerHTML = '<option value="">Select Year</option>';
        
        // Hide all optional fields
        jcFields.style.display = "none";
        document.getElementById('yearGroup').style.display = "none";
        document.getElementById('pgNote').style.display = 'none';

        if (!level) return;

        // Populate courses
        if (courses[level]) {
            courses[level].forEach(course => {
                const option = document.createElement('option');
                option.value = course;
                option.textContent = course;
                courseSelect.appendChild(option);
            });
        }

        // Show relevant fields
        if (level === "JC") {
            jcFields.style.display = "block";
        } else if (level === "UG" || level === "PG") {
            document.getElementById('yearGroup').style.display = "block";
            
            // Populate years
            if (years[level]) {
                years[level].forEach(year => {
                    const option = document.createElement('option');
                    option.value = year;
                    option.textContent = year;
                    yearSelect.appendChild(option);
                });
            }
            
            if (level === "PG") {
                document.getElementById('pgNote').style.display = 'block';
            }
        }
    });

    // Form submission
    visitorForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

        // Prepare data
        const formData = {
            name: document.getElementById("name").value.trim(),
            roll_no: document.getElementById("roll_no").value.trim().toUpperCase(),
            level: levelSelect.value,
            purpose: document.getElementById("purpose").value
        };
        
        // Add course and year based on level
        if (levelSelect.value === "JC") {
            formData.course = "Junior College";
            formData.jc_year = jcYearSelect.value;
            formData.jc_stream = jcStreamSelect.value;
            formData.year = null;
        } else {
            formData.course = courseSelect.value;
            formData.year = yearSelect.value || null;
            formData.jc_year = null;
            formData.jc_stream = null;
        }

        try {
            const res = await fetch("/student/visit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData)
            });

            const result = await res.json();

            if (res.status === 201) {
                alert("Visit recorded successfully!");
                
                // Reset form
                visitorForm.reset();
                courseSelect.innerHTML = '<option value="">Select Course / Stream</option>';
                yearSelect.innerHTML = '<option value="">Select Year</option>';
                document.getElementById('yearGroup').style.display = "none";
                jcFields.style.display = "none";
                jcYearSelect.value = "";
                jcStreamSelect.value = "";
                document.getElementById('pgNote').style.display = 'none';
                
                document.getElementById("name").focus();
            } else {
                alert(result.error || "Failed to record visit");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Connection error. Please try again.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });

    // Auto-focus first input
    document.getElementById("name").focus();
});