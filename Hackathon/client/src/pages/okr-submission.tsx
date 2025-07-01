import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import { useForm, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Sparkles, Target, Clock, Flag, CheckCircle, Loader2, Award } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useLocation } from "wouter";
import { InsertOkr, Okr } from "@shared/schema";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { fadeIn, slideUp, scaleIn, celebrate } from "@/lib/animations";

type SubmissionState = "form" | "processing" | "parsed" | "success";

interface ParsedOkr {
  objective: string;
  deliverables: string[];
  timeline: string;
  tasks: Array<{
    task: string;
    due: string;
    evidence_hint: string;
    level: string;
  }>;
}

// Define the expected response type for creating an OKR from the backend
interface CreateOkrResponse {
  parsed: { // This structure should match the 'parsed' object returned from your backend's process_okr
    objective: string;
    deliverables: string[]; // Or 'key_results' if that's what your backend actually returns
    deadline: string;
    key_results: string[];
  };
  micro_tasks: Array<{
    task: string;
    due: string;
    evidence_hint: string;
    level: string;
  }>;
}

const OkrSubmission = () => {
  const [, navigate] = useLocation();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [submissionState, setSubmissionState] = useState<SubmissionState>("form");
  const [parsedOkr, setParsedOkr] = useState<ParsedOkr | null>(null);

  const form = useForm<InsertOkr>({
    defaultValues: {
      title: "",
      description: "",
      targetDate: new Date(), // Initialize with a Date object
    },
  });

  const createOkrMutation = useMutation<CreateOkrResponse, Error, InsertOkr>({
    mutationFn: async (data) => {
      console.log("Type of data.targetDate before API call:", typeof data.targetDate);
      console.log("Value of data.targetDate before API call:", data.targetDate);
      const response = await apiRequest("POST", "/api/process_okr", {
        title: data.title,
        description: data.description,
        targetDate: data.targetDate.toISOString().split('T')[0],
      }) as CreateOkrResponse;
      return response;
    },
    onSuccess: (response) => {
      setSubmissionState("processing");

      // Simulate parsing process
      setTimeout(() => {
        const mockParsed: ParsedOkr = {
          objective: form.getValues("title"),
          deliverables: response.parsed.key_results || extractDeliverables(form.getValues("description")),
          timeline: new Date(form.getValues("targetDate")).toLocaleDateString(),
          tasks: response.micro_tasks || []
        };
        setParsedOkr(mockParsed);
        setSubmissionState("parsed");

        // Auto advance to success after showing parsed results
        setTimeout(() => {
          setSubmissionState("success");
          queryClient.invalidateQueries({ queryKey: ["/api/get-okrs"] });
        }, 3000);
      }, 2000);
    },
    onError: (error: Error) => {
      const errorMessage = error.message || "Failed to create OKR. Please try again.";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    },
  });

  const handleSubmit: SubmitHandler<InsertOkr> = (data) => {
    createOkrMutation.mutate(data);
  };

  const extractDeliverables = (description: string): string[] => {
    // Simple extraction logic - in a real app this would be more sophisticated
    const matches = description.match(/\d+/g);
    const count = matches ? parseInt(matches[0]) : 3;

    if (description.toLowerCase().includes("article") || description.toLowerCase().includes("blog")) {
      return Array.from({ length: count }, (_, i) => `Article ${i + 1}`);
    } else if (description.toLowerCase().includes("project")) {
      return Array.from({ length: count }, (_, i) => `Project ${i + 1}`);
    }

    return ["Research and Planning", "Core Development", "Review and Finalization"];
  };

  return (
    <motion.div
      className="min-h-screen pt-20 px-6 pb-6 relative z-10"
      variants={fadeIn}
      initial="initial"
      animate="animate"
    >
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <motion.div
          className="flex items-center space-x-4 mb-8"
          variants={slideUp}
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/")}
            className="glass-effect text-white hover:bg-white/10"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-white">Create New OKR</h1>
            <p className="text-white/80">Define your objective and let AI generate actionable tasks</p>
          </div>
        </motion.div>

        <AnimatePresence mode="wait">
          {submissionState === "form" && (
            <motion.div
              key="form"
              variants={scaleIn}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <Card className="glass-card rounded-3xl p-8">
                <CardContent className="p-0">
                  <Form {...form}>
                    <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">

                      {/* OKR Title */}
                      <FormField
                        control={form.control}
                        name="title"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="flex items-center text-lg font-semibold">
                              <Target className="w-5 h-5 mr-2 text-indigo-600" />
                              Objective Title
                            </FormLabel>
                            <FormControl>
                              <Input
                                placeholder="e.g., Publish 3 AI articles by Q4"
                                className="text-lg py-3"
                                {...field}
                              />
                            </FormControl>
                            <FormDescription>
                              A clear and concise statement of what you want to achieve
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      {/* OKR Description */}
                      <FormField
                        control={form.control}
                        name="description"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel className="flex items-center text-lg font-semibold">
                              <Sparkles className="w-5 h-5 mr-2 text-purple-600" />
                              Detailed Description
                            </FormLabel>
                            <FormControl>
                              <Textarea
                                placeholder="Describe your objective in detail. Include specific deliverables, success criteria, and any relevant context. The more detail you provide, the better AI can generate actionable micro-tasks."
                                className="min-h-32 text-base resize-none"
                                {...field}
                              />
                            </FormControl>
                            <FormDescription>
                              Our AI will analyze this description to generate micro-tasks and timelines
                            </FormDescription>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      {/* Target Date and Priority */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <FormField
                          control={form.control}
                          name="targetDate"
                          render={({ field }) => (
                            <FormItem>
                              <FormLabel className="flex items-center text-lg font-semibold">
                                <Clock className="w-5 h-5 mr-2 text-rose-600" />
                                Target Completion Date
                              </FormLabel>
                              <FormControl>
                                <Input
                                  type="date"
                                  className="text-lg py-3"
                                  value={field.value instanceof Date ? field.value.toISOString().split('T')[0] : field.value}
                                  onChange={field.onChange}
                                />
                              </FormControl>
                              <FormDescription>
                                The date you aim to complete this objective and all its tasks
                              </FormDescription>
                              <FormMessage />
                            </FormItem>
                          )}
                        />
                      </div>

                      {/* Submit Button */}
                      <motion.div
                        className="pt-6"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Button
                          type="submit"
                          className="w-full bg-gradient-to-r from-green-500 to-teal-500 hover:from-green-600 hover:to-teal-600 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition-all duration-300 transform hover:-translate-y-1 flex items-center justify-center"
                          disabled={createOkrMutation.isPending}
                        >
                          {createOkrMutation.isPending && <Loader2 className="mr-2 h-5 w-5 animate-spin" />}
                          Generate Micro-Tasks
                          {!createOkrMutation.isPending && (
                            <Sparkles className="w-4 h-4 ml-2 opacity-80 group-hover:opacity-100 transition-opacity duration-300" />
                          )}
                        </Button>
                      </motion.div>
                    </form>
                  </Form>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {submissionState === "processing" && (
            <motion.div
              key="processing"
              variants={scaleIn}
              initial="initial"
              animate="animate"
              exit="exit"
              className="text-center py-20"
            >
              <Loader2 className="w-20 h-20 text-white animate-spin mx-auto mb-6" />
              <h2 className="text-4xl font-bold text-white mb-4">Analyzing your Objective...</h2>
              <p className="text-white/80 text-lg">Please wait while our AI breaks down your OKR into actionable micro-tasks.</p>
            </motion.div>
          )}

          {submissionState === "parsed" && parsedOkr && (
            <motion.div
              key="parsed"
              variants={scaleIn}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <Card className="glass-card rounded-3xl p-8">
                <CardContent className="p-0">
                  <h2 className="text-3xl font-bold text-white mb-6">AI-Generated Tasks</h2>
                  <p className="text-white/80 mb-8">Review the generated tasks and confirm to finalize your OKR.</p>
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-2 flex items-center"><Target className="w-5 h-5 mr-2 text-indigo-500" /> Objective:</h3>
                      <p className="text-white/90 text-lg">{parsedOkr.objective}</p>
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-2 flex items-center"><Flag className="w-5 h-5 mr-2 text-emerald-500" /> Key Results:</h3>
                      <ul className="list-disc list-inside text-white/90 space-y-1">
                        {parsedOkr.deliverables.map((deliverable, index) => (
                          <li key={index}>{deliverable}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-2 flex items-center"><Clock className="w-5 h-5 mr-2 text-rose-500" /> Target Timeline:</h3>
                      <p className="text-white/90">{parsedOkr.timeline}</p>
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-4 flex items-center"><CheckCircle className="w-5 h-5 mr-2 text-blue-500" /> Micro-Tasks:</h3>
                      <div className="space-y-4">
                        {parsedOkr.tasks.map((task, index) => (
                          <div key={index} className="flex items-start bg-white/5 p-4 rounded-xl shadow-sm">
                            <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-1" />
                            <div className="flex-1 ml-3">
                              <p className="font-medium text-white">{task.task}</p>
                              {task.evidence_hint && (
                                <p className="text-white/70 text-sm">{task.evidence_hint}</p>
                              )}
                              {task.due && (
                                <p className="text-white/60 text-xs mt-1">
                                  Due: {new Date(task.due).toLocaleDateString()}
                                </p>
                              )}
                            </div>
                            {task.level && (
                              <Badge variant="outline" className="text-xs h-fit bg-white/10 text-white/80 border-white/20">
                                {task.level}
                              </Badge>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                    <Button
                      onClick={() => setSubmissionState("success")}
                      className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition-all duration-300 transform hover:-translate-y-1 mt-6 flex items-center justify-center"
                    >
                      <CheckCircle className="w-5 h-5 mr-2" />
                      Confirm & Finalize OKR
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {submissionState === "success" && (
            <motion.div
              key="success"
              variants={celebrate}
              initial="initial"
              animate="animate"
              exit="exit"
              className="text-center py-20"
            >
              <Award className="w-24 h-24 text-yellow-400 mx-auto mb-6 drop-shadow-lg" />
              <h2 className="text-5xl font-bold text-white mb-4 leading-tight">OKR Successfully Created!</h2>
              <p className="text-white/80 text-xl mb-8">Your objective is now live and your tasks are ready to be tackled. Let's achieve greatness!</p>
              <Button
                onClick={() => navigate("/")}
                className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white font-bold py-3 px-8 rounded-xl shadow-lg transition-all duration-300 transform hover:-translate-y-1"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Go to Dashboard
              </Button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default OkrSubmission;
