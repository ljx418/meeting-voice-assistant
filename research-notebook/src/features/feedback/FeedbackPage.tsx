import { UnsupportedFeatureState } from '../../shared/components/StateBlock';

export function FeedbackPage() {
  return (
    <UnsupportedFeatureState title="反馈入口位于回答和上下文附近">
      当前版本提供轻量反馈入口，分布在工作区回答、会话回答和图谱上下文附近。质量治理控制台仍属于后续能力。
    </UnsupportedFeatureState>
  );
}
