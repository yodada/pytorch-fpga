#include <ATen/ATen.h>
#include <ATen/Context.h>
#include <ATen/Dispatch.h>
#include <ATen/opencl/OpenCLContext.h>
#include <ATen/opencl/OpenCLEvent.h>
#include <c10/opencl/OpenCLStream.h>
#include <c10/opencl/OpenCLGuard.h>
#include <ATen/opencl/PinnedMemoryAllocator.h>
#include <ATen/native/opencl/Utils.h>
#include <ATen/native/Fill.h>
#include <ATen/native/TensorIterator.h>
#include <ATen/native/DispatchStub.h>

namespace at { namespace native {

void fill_kernel_opencl(TensorIterator& iter, Scalar value) {
  if (iter.numel() == 0) {
    return;
  }
  Tensor self = iter.tensor(0);
  TensorImpl* self_ = checked_tensor_unwrap(self, "self", 2, "fill_kernel_opencl", false, c10::Backend::OpenCL, iter.dtype());
  AT_DISPATCH_ALL_TYPES_AND3(at::ScalarType::Bool, at::ScalarType::Half, at::ScalarType::BFloat16, iter.dtype(), "fill_opencl", [&]() {
    auto value_converted = value.to<scalar_t>();
    auto kernel_name = "cast_s";
    auto kernel_opt = c10::opencl::opencl_kernel(kernel_name);
    TORCH_INTERNAL_ASSERT(kernel_opt.has_value(), "Kernel not found \"", kernel_name, "\"");
    auto stream = at::opencl::getCurrentOpenCLStream(self_->device().index());
    auto kernel = kernel_opt.value();
    AT_OPENCL_CHECK(c10::opencl::runKernel(kernel, {*stream.stream(), self_->numel(), 1},
        value_converted,
        *toBuffer(self_->data()),
        getOpenCLKernelCastType(iter.dtype())));
    C10_OPENCL_CHECK(syncOpenCLPointer(self_->data()));
  });
}

REGISTER_DISPATCH(fill_stub, &fill_kernel_opencl);

} // namespace native
} // namespace at
