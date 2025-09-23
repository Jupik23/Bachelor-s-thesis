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
  justify-content: center;
  align-items: center;
  gap: 5rem;
  padding: 4rem 2rem;
}
.content-container{
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.welcome-header{
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.2;
  color: #2c3e50;
  margin-bottom: 2rem;
}
.welcome-paragraph{
  width: 50rem;
  font-size: 1.25rem;
  color:#7f8c8d;
  margin-top: 1rem;
}
.well-plan-image{
  margin-top: 8%;
  width: 50rem;
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
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}
.btn-primary {
  background-color: #27ae60;
  color: white;
}
.btn-primary:hover {
  background-color: #229954;
  transform: translateY(-2px);
}
.btn-secondary {
  background-color: #ecf0f1;
  color: #2c3e50;
  border: 1px solid #bdc3c7;
}
.btn-secondary:hover {
  background-color: #dcdde1;
}
</style>