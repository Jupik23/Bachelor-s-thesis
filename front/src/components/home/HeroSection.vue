<template>
    <main class="hero-section">
        <div class="content-container">
            <h1 class="welcome-header"> Your Complete Health <br>Companion</h1>
            <p class="welcome-paragraph">The first comprehensive platform that seamlessly integrates diet and <br>
            medication management, with intelligent interaction monitoring for<br> 
            people with special health needs.
            </p>
            <div class="start-button">
            <button class="btn btn-primary">Start Your Health Journey</button>
            <button class="btn btn-secondary">Learn More</button>
            </div>
        </div>
        <div>
            <img src="@/assets/images/wellPlan.jpg" class="well-plan-image"></img>
        </div>
    </main>
</template>

<style scoped>
.hero-section{
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 2rem;
  padding: 4rem 2rem;
}
.content-container{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.welcome-header{
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--text-color-dark);
  margin-bottom: 2rem;
}
.welcome-paragraph{
  width: 90%;
  max-width: 50rem;
  height: auto;
  font-size: 1.25rem;
  color: var(--text-color-subtle);
  margin-top: 1rem;
}
.well-plan-image{
  margin-top: 8%;
  width: 100%;
  max-width: 50rem;
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
}
.start-button{
  display: flex;
  gap: 1rem;
  margin-top: 0.2rem;
}
.well-plan-image{
  border-radius: 1rem;
  box-shadow: 0 10px 20px rgba(0,0,0,0.1),
}
.btn {
  padding: 12px 24px;
  border-radius: var(--border-radius-md);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-primary {
  background-color: var(--primary-color);
  color: var(--white-color);
}
.btn-primary:hover {
  background-color: var(--primary-color-hover);
  transform: translateY(-2px);
}
.btn-secondary {
  background-color: var(--secondary-color);
  color: var(--text-color-dark);
  border: 1px solid var(--border-color);
}
.btn-secondary:hover {
  background-color: var(--secondary-color-hover);
}
</style>