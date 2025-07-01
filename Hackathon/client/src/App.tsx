import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import Dashboard from "@/pages/dashboard";
import OkrSubmission from "@/pages/okr-submission";
import TaskCompletion from "@/pages/task-completion";
import FloatingParticles from "@/components/floating-particles";
import OkrDetails from "@/pages/okr-details";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route path="/okr/new" component={OkrSubmission} />
      <Route path="/task/:id/complete" component={TaskCompletion} />
      <Route path="/okr/:id" component={OkrDetails} />
      <Route component={Dashboard} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500">
          <FloatingParticles />
          <Toaster />
          <Router />
        </div>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
