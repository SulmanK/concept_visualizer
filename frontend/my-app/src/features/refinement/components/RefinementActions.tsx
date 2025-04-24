import React from "react";
import { Button } from "../../../components/ui/Button";

interface RefinementActionsProps {
  onReset: () => void;
  onCreateNew: () => void;
  refinedConceptId?: string;
  selectedColor?: string | null;
}

/**
 * Button actions for the refinement results
 */
export const RefinementActions: React.FC<RefinementActionsProps> = ({
  onReset,
  onCreateNew,
  refinedConceptId,
  selectedColor,
}) => {
  return (
    <div className="flex justify-between mb-4">
      <Button variant="outline" onClick={onReset}>
        Refine Again
      </Button>
      <Button variant="primary" onClick={onCreateNew}>
        Create New Concept
      </Button>
    </div>
  );
};
